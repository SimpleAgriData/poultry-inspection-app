type SectionNumber = number;

type ChecklistCycle = "rearing" | "fattening";
type NoteType =
	| "vaccination"
	| "treatment"
	| "feeding"
	| "relocation"
	| "sock_test"
	| "other"
	| "slaughter"
	| "catching";
type GeneralNoteType = Exclude<NoteType, "slaughter" | "catching">;
type FinishNoteType = Extract<NoteType, "slaughter" | "catching">;
type VaccinationCode = "nd" | "gumboro" | "ib" | "kokzidien";
type TreatmentCode =
	| "amproline"
	| "pyanosid"
	| "lincospectin"
	| "phenoxypen_wsp"
	| "baytril"
	| "lanflox"
	| "amoxicillin"
	| "aviapen"
	| "baycox"
	| "biocillin"
	| "dozuril"
	|  "enro_sleecol"
	|  "enroxal"
	| "neomycinsulfat"
	| "octacillin"
	| "parofor"
	| "pharmasin"
	| "rhemox_forte"
	| "solomocta"
	| "t_s_sol"
	| "toltra_k";
type TreatmentAmountUnit = "l/1000" | "g/1000" | "ml" | "mg" | "l" | "kg";
type WaitingTimeUnit = "day" | "week";
type SockTestResult = "positive" | "negative";
type WeatherCondition =
	| "sun"
	| "cloudy"
	| "precipitation"
	| "extreme_wetness"
	| "frost"
	| "strong_wind";

type ParentFlockEntry = {
	herdIdentifier: string;
	productionWeek: number;
};

type SectionInstallationDetails = {
	sectionNumber: number;
	initialAnimalsCount: number;
	initialWeightGrams: number;
	bedding: string;
	parentFlocks: ParentFlockEntry[];
};

type GeneralNoteEntry = {
	id: string;
	noteType: GeneralNoteType;
	noteText: string | null;
	deliveryReceiptNumber: string | null;
	batchNumber: string | null;
	vaccinationCode: VaccinationCode | null;
	treatmentCode: TreatmentCode | null;
	treatmentAmountValue: number | null;
	treatmentAmountUnit: TreatmentAmountUnit | null;
	treatmentWaitingTimeValue: number | null;
	treatmentWaitingTimeUnit: WaitingTimeUnit | null;
	sockTestResult: SockTestResult | null;
	slaughterDate: Date | null;
	slaughterAnimalsCount: number | null;
	slaughterFinalWeightKg: number | null;
	slaughtererName: string | null;
	catchingTime: string | null;
	catcherName: string | null;
};

type FinishNoteEntry = {
	id: string;
	noteType: FinishNoteType;
	noteText: string | null;
	deliveryReceiptNumber: string | null;
	batchNumber: string | null;
	vaccinationCode: VaccinationCode | null;
	treatmentCode: TreatmentCode | null;
	treatmentAmountValue: number | null;
	treatmentAmountUnit: TreatmentAmountUnit | null;
	treatmentWaitingTimeValue: number | null;
	treatmentWaitingTimeUnit: WaitingTimeUnit | null;
	sockTestResult: SockTestResult | null;
	slaughterDate: Date | null;
	slaughterAnimalsCount: number | null;
	slaughterFinalWeightKg: number | null;
	slaughtererName: string | null;
	catchingTime: string | null;
	catcherName: string | null;
};

type StallkarteCommands = {
	"assign-fattening-farm": { stallkarteId: number; farmId: number };
	"assign-rearing-farm": { stallkarteId: number; farmId: number };
	"delete-stallkarte": { stallkarteId: number };
	"finish-stallkarte": {
		stallkarteId: number;
		dateFinished: Date;
		finishNotes: FinishNoteEntry[];
	};
	"save-finish-notes": {
		stallkarteId: number;
		finishNotes: FinishNoteEntry[];
	};
	"save-general-notes": {
		stallkarteId: number;
		productionDay: number;
		generalNotes: GeneralNoteEntry[];
	};
	"log-section-note": {
		stallkarteId: number;
		productionDay: number;
		sectionNumber: number;
		note: string;
	};
	"record-ambient-climate": {
		stallkarteId: number;
		productionDay: number;
		temperatureCelsius: number | null;
		humidityPercent: number | null;
	};
	"record-feed-consumption": {
		stallkarteId: number;
		productionDay: number;
		amountKg: number;
	};
	"record-fattening-day-data": {
		stallkarteId: number;
		productionDay: number;
		openingTime: string | null;
		weatherConditions: WeatherCondition[];
		veterinarian: boolean;
	};
	"record-mortality": {
		stallkarteId: number;
		productionDay: number;
		sectionNumber: number;
		naturalDeaths: number | null;
		selectiveDeaths: number | null;
		shift: "morning" | "evening";
	};
	"record-water-consumption": {
		stallkarteId: number;
		productionDay: number;
		amountLiters: number;
	};
	"record-weight": {
		stallkarteId: number;
		productionDay: number;
		weightGrams: number;
	};
	"reopen-stallkarte": {
		stallkarteId: number;
	};
	"transfer-flock": {
		stallkarteId: number;
		transferDate: Date;
		animalsBySectionNumber: Record<SectionNumber, number>;
	};
	"revise-transfer-details": {
		stallkarteId: number;
		animalsBySectionNumber: Record<SectionNumber, number>;
	};
	"start-stallkarte": {
		dateStarted: Date;
		dateHatched: Date;
		hatcheryName: string;
		breed: string;
		fatteningCycle: string;
		ecoControlNumber: string;
		isEuBio: boolean;
		isNaturland: boolean;
	};
	"replace-installation-details": {
		stallkarteId: number;
		sectionDetails: SectionInstallationDetails[];
	};
	"revise-details": {
		stallkarteId: number;
		dateHatched: Date;
		hatcheryName: string;
		breed: string;
		fatteningCycle: string;
		isEuBio: boolean;
		isNaturland: boolean;
	};
	"perform-light-program": {
		stallkarteId: number;
		cycle: ChecklistCycle;
		didDarkPeriodTest: boolean | null;
		hadDivergenceDueToVet: boolean | null;
	};
	"perform-alarm-test": {
		stallkarteId: number;
		cycle: ChecklistCycle;
		didEmergencyPowerTest: boolean | null;
		didAlarmTest: boolean | null;
	};
	"apply-pest-control-measures": {
		stallkarteId: number;
		cycle: ChecklistCycle;
		didPerformPestControl: boolean | null;
		annotation: string | null;
	};
	"clean-silo": {
		stallkarteId: number;
		cycle: ChecklistCycle;
		date: Date | null;
		detergent: string | null;
		dosis: string | null;
	};
	"disinfect-stable": {
		stallkarteId: number;
		cycle: ChecklistCycle;
		date: Date | null;
		disinfectant: string | null;
		dosis: string | null;
	};
	"disinfect-water-line": {
		stallkarteId: number;
		cycle: ChecklistCycle;
		date: Date | null;
		disinfectant: string | null;
		dosis: string | null;
	};
};

type StallkarteCommand = keyof StallkarteCommands;

export type { StallkarteCommand, StallkarteCommands };
