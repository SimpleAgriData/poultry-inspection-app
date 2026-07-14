const allNonNull = <T>(arr: (T | null | undefined)[]): arr is T[] => {
	return arr.every((item) => item !== null && item !== undefined);
};

export { allNonNull };
