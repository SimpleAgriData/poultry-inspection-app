interface Milestone {
	description: string;
}

interface Milestones {
	[productionDay: number]: Milestone;
}

const milestones: Milestones = {
	7: {
		description: "Bitte den Qualitätsbericht Bio-Küken nach dem 7. Lebenstag zurücksenden",
	},
	39: {
		description:
			"Bitte den rechtzeitigen Zeitpunkt für Sockenproben beachten (Spätestens 10 Tage vor der Schlachtung Proben versenden!)",
	},
	46: {
		description:
			"Bitte den rechtzeitigen Zeitpunkt für Sockenproben beachten (Spätestens 10 Tage vor der Schlachtung Proben versenden!)",
	},
};

const getMilestoneForProductionDay = (productionDay: number): Milestone | null => {
	return milestones[productionDay] || milestones[productionDay - 1] || null;
};

export type { Milestone, Milestones };
export { getMilestoneForProductionDay };
