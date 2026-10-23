export default function GradeBadge({ grade }) {
  const color = grade === "VIP" ? "gold" : "gray";
  return <span style={{ color }}>{grade}</span>;
}
