export function invertMap(sourceMap: Record<string, number>): Record<string, string> {
  const targetMap: Record<string, string> = {};
  Object.entries(sourceMap).forEach(([key, value]) => {
    targetMap[String(value)] = key;
  });
  return targetMap;
}

export function parseEnumList(
  rawValue: string,
  enumMap: Record<string, number>,
  label: string,
): number[] {
  const values = rawValue
    .split(",")
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean);

  if (values.length === 0) {
    throw new Error(`${label} cannot be empty`);
  }

  return values.map((value) => {
    if (!(value in enumMap)) {
      throw new Error(
        `Unknown ${label} value '${value}'. Allowed: ${Object.keys(enumMap).join(", ")}`,
      );
    }
    return enumMap[value];
  });
}
