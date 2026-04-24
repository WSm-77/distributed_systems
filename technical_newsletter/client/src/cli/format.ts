import type { EventMessage } from "./proto";

export interface FormattedEvent {
  id: string;
  title: string;
  category: string | number;
  skillLevel: string | number;
  location: string;
  date: string;
}

export function formatEvent(
  event: EventMessage,
  eventTypesByValue: Record<string, string>,
  skillLevelsByValue: Record<string, string>,
): FormattedEvent {
  const categoryValue = event.getCategory();
  const skillLevelValue = event.getSkillLevel();
  const location = event.getLocation();

  const categoryName = eventTypesByValue[String(categoryValue)] ?? categoryValue;
  const skillName = skillLevelsByValue[String(skillLevelValue)] ?? skillLevelValue;

  const city = location?.getCity() ?? "";
  const country = location?.getCountry() ?? "";

  return {
    id: event.getId(),
    title: event.getTitle(),
    category: categoryName,
    skillLevel: skillName,
    location: `${city}, ${country}`.replace(/^,\s*|,\s*$/g, ""),
    date: event.getDate(),
  };
}
