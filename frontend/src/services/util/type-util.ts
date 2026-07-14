/**
 * Coerces undefined to null. This is useful for APIs that expect null instead of undefined. Otherwise, it returns the value as is.
 * @param value
 */
const coerceNull = <T>(value: T | null | undefined): T | null => {
	if (value === undefined) {
		return null;
	}
	return value;
};

export { coerceNull };
