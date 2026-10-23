# -*- coding: utf-8 -*-
# 동네카페 정책 숫자 모음. 정책이 바뀌면 여기만 고쳐요.

# 등급별 적립률
POINT_RATES = {"일반": 0.01, "VIP": 0.03}

# 누적 결제가 이 금액 이상이면 해당 등급 (높은 등급부터 적어요). 등급을 더할 때는 여기와 POINT_RATES에 한 줄씩 더해요.
GRADE_THRESHOLDS = (("VIP", 100000),)
VIP_THRESHOLD = 100000

# 생일 쿠폰: 생일이 있는 달 첫 주문이 최소 주문 금액 이상이면 할인
BIRTHDAY_COUPON_AMOUNT = 3000
BIRTHDAY_COUPON_MIN_ORDER = 5000

# 포인트는 이 점수부터 쓸 수 있어요
MIN_USE_POINTS = 1000

# 크리스마스 이벤트: 이 날짜는 적립 두 배
EVENT_DOUBLE_DATES = ("2020-12-25",)

# 사장님 비번 (바꾸면 키오스크도 바꿔야 함)
ADMIN_PASSWORD = "cafe1234"
