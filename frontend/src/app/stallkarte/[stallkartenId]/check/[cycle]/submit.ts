import type { ChecklistFormData } from "@/app/stallkarte/[stallkartenId]/check/[cycle]/page";
import { apiService } from "@/services/api";
import type { StallkarteCommands } from "@/services/api/stallkarte/commands";
import {
	getStallkarteChecklist,
	type Stallkarte,
	type StallkarteAlarmTest,
	type StallkarteLightingProgram,
	type StallkartePestControlMeasures,
	type StallkarteSiloCleaned,
	type StallkarteStableDisinfected,
	type StallkarteWaterLineDisinfected,
} from "@/services/domain/stallkarte";
import { dateUtil } from "@/services/util/date-util";

type ChecklistCommandNames =
	| "perform-light-program"
	| "perform-alarm-test"
	| "apply-pest-control-measures"
	| "clean-silo"
	| "disinfect-stable"
	| "disinfect-water-line";

type CommandData<K extends ChecklistCommandNames> = Omit<
	StallkarteCommands[K],
	"stallkarteId" | "cycle"
>;

const getAlarmTestCommand = (
	existingAlarmTest: StallkarteAlarmTest | null,
	formData: ChecklistFormData,
): CommandData<"perform-alarm-test"> | null => {
	const existingDidEmergencyPowerTest = existingAlarmTest?.didEmergencyPowerTest ?? null;
	const existingDidAlarmTest = existingAlarmTest?.didAlarmTest ?? null;

	const didEmergencyPowerTestChange =
		existingDidEmergencyPowerTest !== formData.didEmergencyPowerTest;
	const didAlarmTestChange = existingDidAlarmTest !== formData.didAlarmTest;

	const hasChanges = didEmergencyPowerTestChange || didAlarmTestChange;

	if (!hasChanges) {
		return null;
	}

	return {
		didEmergencyPowerTest: formData.didEmergencyPowerTest,
		didAlarmTest: formData.didAlarmTest,
	};
};

const getLightProgramCommand = (
	existingLightingProgram: StallkarteLightingProgram | null,
	formData: ChecklistFormData,
): CommandData<"perform-light-program"> | null => {
	const existingDidDarkPeriodTest = existingLightingProgram?.didDarkPeriodTest ?? null;
	const existingHadDivergenceDueToVet = existingLightingProgram?.hadDivergenceDueToVet ?? null;

	const didDarkPeriodTestChange = existingDidDarkPeriodTest !== formData.didDarkPeriodTest;
	const didDivergenceDueToVetChange =
		existingHadDivergenceDueToVet !== formData.hadDivergenceDueToVet;

	const hasChanges = didDarkPeriodTestChange || didDivergenceDueToVetChange;

	if (!hasChanges) {
		return null;
	}

	return {
		didDarkPeriodTest: formData.didDarkPeriodTest,
		hadDivergenceDueToVet: formData.hadDivergenceDueToVet,
	};
};

const getPestControlMeasuresCommand = (
	existingPestControlMeasures: StallkartePestControlMeasures | null,
	formData: ChecklistFormData,
): CommandData<"apply-pest-control-measures"> | null => {
	const existingDidPerformPestControl = existingPestControlMeasures?.didPerformPestControl ?? null;
	const existingAnnotation = existingPestControlMeasures?.annotation ?? null;

	const didPerformPestControlChange =
		existingDidPerformPestControl !== formData.didPestControlMeasures;
	const annotationChange = existingAnnotation !== formData.pestControlMeasuresAnnotation;

	const hasChanges = didPerformPestControlChange || annotationChange;

	if (!hasChanges) {
		return null;
	}

	return {
		didPerformPestControl: formData.didPestControlMeasures,
		annotation: formData.pestControlMeasuresAnnotation,
	};
};

const getSiloCleanedCommand = (
	existingSiloCleaned: StallkarteSiloCleaned | null,
	formData: ChecklistFormData,
): CommandData<"clean-silo"> | null => {
	const existingDate = existingSiloCleaned?.date ?? null;
	const existingDetergent = existingSiloCleaned?.detergent ?? null;
	const existingDosis = existingSiloCleaned?.dosis ?? null;

	const dateChange =
		dateUtil.optionalStrDate(existingDate) !== dateUtil.optionalStrDate(formData.siloCleaningDate);
	const detergentChange = existingDetergent !== formData.siloCleaningDetergent;
	const dosisChange = existingDosis !== formData.siloCleaningDosis;

	const hasChanges = dateChange || detergentChange || dosisChange;

	if (!hasChanges) {
		return null;
	}

	return {
		date: formData.siloCleaningDate,
		detergent: formData.siloCleaningDetergent,
		dosis: formData.siloCleaningDosis,
	};
};

const getStableDisinfectionCommand = (
	existingStableDisinfection: StallkarteStableDisinfected | null,
	formData: ChecklistFormData,
): CommandData<"disinfect-stable"> | null => {
	const existingDate = existingStableDisinfection?.date ?? null;
	const existingDisinfectant = existingStableDisinfection?.disinfectant ?? null;
	const existingDosis = existingStableDisinfection?.dosis ?? null;

	const dateChange =
		dateUtil.optionalStrDate(existingDate) !==
		dateUtil.optionalStrDate(formData.stableDisinfectionDate);
	const disinfectantChange = existingDisinfectant !== formData.stableDisinfectant;
	const dosisChange = existingDosis !== formData.stableDisinfectantDosis;

	const hasChanges = dateChange || disinfectantChange || dosisChange;

	if (!hasChanges) {
		return null;
	}

	return {
		date: formData.stableDisinfectionDate,
		disinfectant: formData.stableDisinfectant,
		dosis: formData.stableDisinfectantDosis,
	};
};

const getWaterLineDisinfectionCommand = (
	existingWaterLineDisinfection: StallkarteWaterLineDisinfected | null,
	formData: ChecklistFormData,
): CommandData<"disinfect-water-line"> | null => {
	const existingDate = existingWaterLineDisinfection?.date ?? null;
	const existingDisinfectant = existingWaterLineDisinfection?.disinfectant ?? null;
	const existingDosis = existingWaterLineDisinfection?.dosis ?? null;

	const dateChange =
		dateUtil.optionalStrDate(existingDate) !==
		dateUtil.optionalStrDate(formData.waterLineDisinfectionDate);
	const disinfectantChange = existingDisinfectant !== formData.waterLineDisinfectant;
	const dosisChange = existingDosis !== formData.waterLineDisinfectantDosis;

	const hasChanges = dateChange || disinfectantChange || dosisChange;

	if (!hasChanges) {
		return null;
	}

	return {
		date: formData.waterLineDisinfectionDate,
		disinfectant: formData.waterLineDisinfectant,
		dosis: formData.waterLineDisinfectantDosis,
	};
};

type Command<K extends ChecklistCommandNames> = {
	commandName: K;
	data: StallkarteCommands[K];
};

export const submitChecklist = async (
	stallkarte: Stallkarte,
	cycle: "rearing" | "fattening",
	formData: ChecklistFormData,
): Promise<boolean> => {
	const checklist = getStallkarteChecklist(stallkarte.state, cycle);

	const commands: Command<ChecklistCommandNames>[] = [];
	const alarmTestCommand = getAlarmTestCommand(checklist?.alarmTest ?? null, formData);
	const lightProgramCommand = getLightProgramCommand(checklist?.lightingProgram ?? null, formData);
	const pestControlMeasuresCommand = getPestControlMeasuresCommand(
		checklist?.pestControlMeasures ?? null,
		formData,
	);
	const siloCleanedCommand = getSiloCleanedCommand(checklist?.siloCleaned ?? null, formData);
	const stableDisinfectionCommand = getStableDisinfectionCommand(
		checklist?.stableDisinfection ?? null,
		formData,
	);
	const waterLineDisinfectionCommand = getWaterLineDisinfectionCommand(
		checklist?.waterLineDisinfected ?? null,
		formData,
	);

	const addCommandIfNotNull = <K extends ChecklistCommandNames>(
		command: CommandData<K> | null,
		commandName: K,
	) => {
		if (!command) return;
		commands.push({
			commandName,
			data: {
				stallkarteId: stallkarte.id,
				cycle: cycle,
				...command,
			} as StallkarteCommands[K],
		});
	};

	addCommandIfNotNull(alarmTestCommand, "perform-alarm-test");
	addCommandIfNotNull(lightProgramCommand, "perform-light-program");
	addCommandIfNotNull(pestControlMeasuresCommand, "apply-pest-control-measures");
	addCommandIfNotNull(siloCleanedCommand, "clean-silo");
	addCommandIfNotNull(stableDisinfectionCommand, "disinfect-stable");
	addCommandIfNotNull(waterLineDisinfectionCommand, "disinfect-water-line");

	if (commands.length === 0) {
		return false;
	}

	const promises: Promise<unknown>[] = [];

	for (const { commandName, data } of commands) {
		const promise = apiService.stallkarte.runCommand(commandName, data);
		promises.push(promise);
	}

	await Promise.allSettled(promises);
	return true;
};
