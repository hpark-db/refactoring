# -*- coding: utf-8 -*-
"""cafe.py를 복사본에서 돌려 tests/expected/<사례>/ 의 기록과 비교해요.

    python3 tests/verify.py

사례 두 개를 확인해요.
  basic  data/ 의 실제 입력 (비회원, 생일 쿠폰, 포인트 사용, VIP 승급)
  edge   tests/cases/edge/data/ (크리스마스 두 배, 같은 달 두 번째 주문,
         1,000점 미만 사용, 보유 초과 사용, 5,000원 미만 생일 주문)
화면 출력, out/members.csv, out/report.txt, 종료 코드를 비교하고
입력 파일이 바뀌지 않았는지도 봐요. 기록은 원본 코드로 만들었어요.
"""
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = {
    "basic": os.path.join(ROOT, "data"),
    "edge": os.path.join(ROOT, "tests", "cases", "edge", "data"),
}


def norm(text):
    return text.replace("\r\n", "\n").rstrip("\n")


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return norm(f.read())
    except FileNotFoundError:
        return None


def run_case(name, data_dir):
    expected = os.path.join(ROOT, "tests", "expected", name)
    work = tempfile.mkdtemp(prefix="cafe-verify-")
    fails = []
    try:
        for f in os.listdir(ROOT):
            if f.endswith(".py"):
                shutil.copy(os.path.join(ROOT, f), work)
        shutil.copytree(data_dir, os.path.join(work, "data"))
        run = subprocess.run([sys.executable, "cafe.py"], cwd=work,
                             capture_output=True, text=True, encoding="utf-8")
        if run.returncode != 0:
            fails.append("종료 코드 %d (기대 0)\n%s" % (run.returncode, run.stderr))
        if norm(run.stdout) != read(os.path.join(expected, "stdout.txt")):
            fails.append("화면 출력이 달라요")
        for f in ("members.csv", "report.txt"):
            if read(os.path.join(work, "out", f)) != read(os.path.join(expected, f)):
                fails.append("out/%s 가 달라요" % f)
        for f in os.listdir(data_dir):
            if not filecmp.cmp(os.path.join(data_dir, f),
                               os.path.join(work, "data", f), shallow=False):
                fails.append("data/%s 가 바뀌었어요" % f)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return fails


def main():
    passed = 0
    for name, data_dir in CASES.items():
        fails = run_case(name, data_dir)
        if fails:
            print("FAIL", name)
            for msg in fails:
                print("  ", msg)
        else:
            print("OK  ", name)
            passed += 1
    print("통과 %d/%d" % (passed, len(CASES)))
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
