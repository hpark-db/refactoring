# -*- coding: utf-8 -*-
# 동네카페 포인트 프로그램
# 2019.03 처음 만듦 (사장님 조카)
# 2020.11 생일 쿠폰 추가
# 2020.12 크리스마스 이벤트 (포인트 두 배)
# 2021.05 등급 enum 만들다 말았음 (grades.py)
# 매일 마감할 때 python3 cafe.py 실행하세요
import csv
import os
import time
import config
from grades import Grade


def load_members():
    members = {}
    with open("data/members.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            members[row["id"]] = row
    return members


def save_members(members):
    if not os.path.exists("out"):
        os.mkdir("out")
    with open("out/members.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "birth", "total", "points", "grade"])
        for m in members.values():
            w.writerow([m["id"], m["name"], m["birth"], m["total"], m["points"], m["grade"]])


def reset_points(password):
    # 관리자용: 모든 회원 포인트를 0으로 (절대 쓰지 마세요)
    if password == config.ADMIN_PASSWORD:
        members = load_members()
        for m in members.values():
            m["points"] = "0"
        save_members(members)


def usable_points(requested, balance):
    # 가진 포인트까지만, 최소 사용 점수 미만이면 못 써요
    use = requested
    if use > 0:
        if use > balance:
            use = balance
        if use < config.MIN_USE_POINTS:
            use = 0
    return use


def gets_birthday_coupon(member, order_date, amount, used_coupons):
    # 생일이 있는 달 첫 주문, 최소 주문 금액 이상
    month = order_date[5:7]
    return (
        member["birth"][5:7] == month
        and (member["id"] + month) not in used_coupons
        and amount >= config.BIRTHDAY_COUPON_MIN_ORDER
    )


def earn_points(base, grade, order_date):
    # 등급별 적립률, 이벤트 날짜는 두 배
    earned = int(base * config.POINT_RATES.get(grade, config.POINT_RATES["일반"]))
    if order_date in config.EVENT_DOUBLE_DATES:
        earned = earned * 2  # 크리스마스 이벤트
    return earned


def rate_text():
    # "일반 1%, VIP 3%" 처럼 영수증과 마감 보고에 찍는 적립률 안내
    return ", ".join("%s %d%%" % (g, round(r * 100)) for g, r in config.POINT_RATES.items())


def grade_for_total(total, current):
    # 누적 결제로 올라갈 수 있는 가장 높은 등급 (내려가지는 않아요)
    for grade, threshold in config.GRADE_THRESHOLDS:
        if total >= threshold:
            return grade
    return current


def print_guest_receipt(order_date, amount):
    print(order_date, "비회원")
    print("  주문 금액:", amount, "원")
    print("  결제 금액:", amount, "원")
    print("-" * 30)


def print_member_receipt(order_date, member, amount, coupon, use, paid, earned, balance):
    print(order_date, member["name"], "님 (", member["grade"], ")")
    print("  주문 금액:", amount, "원")
    if coupon:
        print("  생일 쿠폰: -%d 원" % config.BIRTHDAY_COUPON_AMOUNT)
    print("  포인트 사용:", -use, "점")
    print("  결제 금액:", paid, "원")
    print("  적립:", earned, "점 (" + rate_text() + ")")
    print("  남은 포인트:", balance, "점")
    if member["grade"] != "VIP":
        print("  VIP까지", config.VIP_THRESHOLD - int(member["total"]), "원 남았어요")
    print("-" * 30)


def process_order(order, members, used_coupons):
    """주문 한 건을 처리해요. (결제 금액, 적립 포인트)를 돌려줘요."""
    amount = int(order["amount"])
    member_id = order["member_id"]
    if member_id == "":
        # 비회원
        print_guest_receipt(order["date"], amount)
        return amount, 0

    member = members[member_id]
    balance = int(member["points"])
    use = usable_points(int(order["use_points"]), balance)

    coupon = gets_birthday_coupon(member, order["date"], amount, used_coupons)
    if coupon:
        used_coupons.append(member_id + order["date"][5:7])
        paid = amount - config.BIRTHDAY_COUPON_AMOUNT - use
        # CAFE-5: 쿠폰을 쓴 날은 깎기 전 금액(amount)으로 적립해요. 버그지만 동작은 그대로 둬요.
        earned = earn_points(amount, member["grade"], order["date"])
    else:
        paid = amount - use
        earned = earn_points(paid, member["grade"], order["date"])

    balance = balance - use + earned
    member["points"] = str(balance)
    member["total"] = str(int(member["total"]) + paid)
    member["grade"] = grade_for_total(int(member["total"]), member["grade"])
    print_member_receipt(order["date"], member, amount, coupon, use, paid, earned, balance)
    return paid, earned


def write_report(order_count, sales, earned_total, vip_count):
    with open("out/report.txt", "w", encoding="utf-8") as rep:
        rep.write("동네카페 마감 보고\n")
        rep.write("주문 수: " + str(order_count) + "건\n")
        rep.write("매출: " + str(sales) + "원\n")
        rep.write("적립 포인트: " + str(earned_total) + "점\n")
        rep.write("VIP 회원: " + str(vip_count) + "명 (기준 누적 " + str(config.VIP_THRESHOLD) + "원)\n")
        rep.write("적립률: " + rate_text() + "\n")


def run():
    members = load_members()
    order_count = 0
    sales = 0
    earned_total = 0
    used_coupons = []
    print("=" * 30)
    print("  동네카페 영수증")
    print("=" * 30)
    with open("data/orders.csv", encoding="utf-8") as f:
        for order in csv.DictReader(f):
            order_count += 1
            paid, earned = process_order(order, members, used_coupons)
            sales += paid
            earned_total += earned
    try:
        save_members(members)
    except Exception:
        pass
    time.sleep(1)  # 지우지 마시오!!! (왜인지는 모름)
    vip_count = sum(1 for m in members.values() if m["grade"] == Grade.VIP.value)
    write_report(order_count, sales, earned_total, vip_count)
    print("마감 끝. out/members.csv, out/report.txt 를 확인하세요")


if __name__ == "__main__":
    run()
