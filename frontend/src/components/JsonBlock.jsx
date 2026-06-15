import { asJson } from "../utils/formatters";

export default function JsonBlock({ value, large = false }) {
  return <pre className={`jsonBlock ${large ? "large" : ""}`}>{asJson(value)}</pre>;
}
