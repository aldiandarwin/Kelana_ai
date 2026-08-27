const budgetFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0,
});

const dateFormatter = new Intl.DateTimeFormat("en-US", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

const destinationIcons: Array<[string, string]> = [
  ["japan", "🗾"],
  ["tokyo", "🗼"],
  ["bali", "🌴"],
  ["labuan bajo", "🐉"],
  ["yogyakarta", "🏛️"],
  ["bandung", "⛰️"],
  ["singapore", "🦁"],
  ["paris", "🗼"],
  ["london", "🎡"],
  ["new york", "🗽"],
  ["sydney", "🌊"],
];

export function formatBudget(value: number): string {
  return "USD " + budgetFormatter.format(value);
}

export function formatTripDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Date unavailable" : dateFormatter.format(date);
}

export function getDestinationIcon(destination: string): string {
  const normalized = destination.trim().toLowerCase();
  return (
    destinationIcons.find(([keyword]) => normalized.includes(keyword))?.[1] ??
    "🧭"
  );
}

export function getCategoryBadgeClasses(category: string): string {
  switch (category.toLowerCase()) {
    case "backpacker":
      return "bg-emerald-100 text-emerald-800";
    case "luxury":
      return "bg-violet-100 text-violet-800";
    default:
      return "bg-amber-100 text-amber-900";
  }
}

export function getTravelStyleBadgeClasses(travelStyle: string): string {
  switch (travelStyle.toLowerCase()) {
    case "family":
      return "border-sky-200 bg-sky-50 text-sky-800";
    case "solo":
      return "border-orange-200 bg-orange-50 text-orange-800";
    case "couple":
      return "border-rose-200 bg-rose-50 text-rose-800";
    default:
      return "border-slate-200 bg-slate-50 text-slate-700";
  }
}
