const intervalIdStore = new Map<string, ReturnType<typeof setTimeout>>();
let intervalIdCounter = 0;

interface FixedDelayIntervalOptions {
	runImmediately?: boolean;
}

const setFixedDelayInterval = (
	callback: () => Promise<void> | void,
	delayMs: number,
	options?: FixedDelayIntervalOptions,
): number => {
	const intervalId = intervalIdCounter++;

	(async () => {
		if (options?.runImmediately) {
			await callback();
		}

		const interval = async () => {
			await callback();
			const id = setTimeout(interval, delayMs);
			intervalIdStore.set(intervalId.toString(), id);
		};
		const id = setTimeout(interval, delayMs);
		intervalIdStore.set(intervalId.toString(), id);
	})();

	return intervalId;
};

const clearFixedDelayInterval = (intervalId: number) => {
	const id = intervalIdStore.get(intervalId.toString());
	if (id) {
		clearTimeout(id);
		intervalIdStore.delete(intervalId.toString());
	}
};

export { clearFixedDelayInterval, setFixedDelayInterval };
