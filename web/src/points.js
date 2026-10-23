// 화면에서 보여 줄 적립 포인트 (cafe.py의 config.POINT_RATES와 같은 규칙으로 맞춰 둘 것)
const VIP_RATE = 0.03;
const NORMAL_RATE = 0.01;

export function calcPoint(amount, grade) {
  return Math.floor(amount * (grade === "VIP" ? VIP_RATE : NORMAL_RATE));
}
