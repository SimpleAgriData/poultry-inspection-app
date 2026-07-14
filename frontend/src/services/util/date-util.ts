type IfExtends<T, U, RIf, RElse> = T extends U ? RIf : RElse;
const strDate = (date: Date): string => date.toISOString().split("T")[0]; // helper function to convert Date to ISO 8601 date string (only date part)

/**
 * Converts a Date to an ISO 8601 date string, or returns null/undefined if the input is null/undefined.
 * @param date
 */
const optionalStrDate = <
	T extends Date | null | undefined,
	TReturn extends IfExtends<T, Date, string, Exclude<T, Date>>,
>(
	date: T,
): TReturn => (!date ? (date as unknown as TReturn) : (strDate(date) as TReturn));

export const dateUtil = {
	strDate,
	optionalStrDate,
};
