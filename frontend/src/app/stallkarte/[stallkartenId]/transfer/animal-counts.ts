import type { Stallkarte, StallkarteStateDaySection } from "@/services/domain/stallkarte";

const getTotalDayMortality = (sectionDay: StallkarteStateDaySection): number => {
	const naturalMortalityMorning = sectionDay.naturalMortalityMorning ?? 0;
	const naturalMortalityEvening = sectionDay.naturalMortalityEvening ?? 0;
	const selectiveMortalityMorning = sectionDay.selectiveMortalityMorning ?? 0;
	const selectiveMortalityEvening = sectionDay.selectiveMortalityEvening ?? 0;

	return (
		naturalMortalityMorning +
		naturalMortalityEvening +
		selectiveMortalityMorning +
		selectiveMortalityEvening
	);
};

const calculateAnimalsBySectionUntilProductionDay = (
	stallkarte: Stallkarte,
	untilProductionDay: number,
): Record<number, number> => {
	if (!stallkarte.state.rearingFarm) {
		return {};
	}

	const animalsBySection: Record<number, number> = {};

	for (const section of stallkarte.state.rearingFarm.sections) {
		animalsBySection[section.number] =
			stallkarte.state.installationDetailsBySection[section.number]?.initialAnimalsCount ?? 0;
	}

	for (const [dayKey, day] of Object.entries(stallkarte.state.days)) {
		const productionDay = Number(dayKey);
		if (productionDay > untilProductionDay) {
			continue;
		}

		for (const daySection of Object.values(day.sections)) {
			const currentCount = animalsBySection[daySection.sectionNumber] ?? 0;
			const nextCount = currentCount - getTotalDayMortality(daySection);
			animalsBySection[daySection.sectionNumber] = nextCount >= 0 ? nextCount : 0;
		}
	}

	return animalsBySection;
};

export { calculateAnimalsBySectionUntilProductionDay };
