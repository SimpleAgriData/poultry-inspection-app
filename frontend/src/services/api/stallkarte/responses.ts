import type { SuccessResponse } from "@/services/api/openapi";

type ResponseStallkarte = Exclude<
	SuccessResponse<"/api/v1/find-stallkarte", "get">["stallkarte"],
	null
>;
type ResponseStallkarteState = ResponseStallkarte["state"];
type ResponseStallkarteTransfer = Exclude<ResponseStallkarteState["transfer"], null>;
type ResponseStallkarteFarm = Exclude<ResponseStallkarteState["fattening_farm"], null>;
type ResponseStallkarteSection = ResponseStallkarteFarm["sections"][number];
type ResponseStallkarteStateDay = ResponseStallkarteState["days"][number];
type ResponseStallkarteStateDaySection = ResponseStallkarteStateDay["sections"][number];
type ResponseStallkarteStateDayNote = ResponseStallkarteStateDay["notes"][number];
type ResponseStallkarteFinishNote = ResponseStallkarteState["finish_notes"][number];
type ResponseStallkarteChecklist = Exclude<ResponseStallkarteState["fattening_checklist"], null>;
type ResponseStallkarteAlarmTest = Exclude<ResponseStallkarteChecklist["alarm_test"], null>;
type ResponseStallkarteLightingProgram = Exclude<
	ResponseStallkarteChecklist["lighting_program"],
	null
>;
type ResponseStallkartePestControlMeasures = Exclude<
	ResponseStallkarteChecklist["pest_control_measures"],
	null
>;
type ResponseStallkarteSiloCleaned = Exclude<ResponseStallkarteChecklist["silo_cleaned"], null>;
type ResponseStallkarteStableDisinfected = Exclude<
	ResponseStallkarteChecklist["stable_disinfected"],
	null
>;
type ResponseStallkarteWaterLineDisinfected = Exclude<
	ResponseStallkarteChecklist["water_line_disinfected"],
	null
>;

type ResponseShallowStallkarte = SuccessResponse<
	"/api/v1/find-my-stallkarten",
	"get"
>["active_stallkarten"][number];

export type {
	ResponseShallowStallkarte,
	ResponseStallkarte,
	ResponseStallkarteAlarmTest,
	ResponseStallkarteChecklist,
	ResponseStallkarteFarm,
	ResponseStallkarteFinishNote,
	ResponseStallkarteLightingProgram,
	ResponseStallkartePestControlMeasures,
	ResponseStallkarteSection,
	ResponseStallkarteSiloCleaned,
	ResponseStallkarteStableDisinfected,
	ResponseStallkarteState,
	ResponseStallkarteStateDay,
	ResponseStallkarteStateDayNote,
	ResponseStallkarteStateDaySection,
	ResponseStallkarteTransfer,
	ResponseStallkarteWaterLineDisinfected,
};
