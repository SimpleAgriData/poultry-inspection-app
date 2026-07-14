const getDaysDiff = (date1: Date, date2: Date): number => {
	const utc1 = Date.UTC(date1.getFullYear(), date1.getMonth(), date1.getDate());
	const utc2 = Date.UTC(date2.getFullYear(), date2.getMonth(), date2.getDate());
	const millisecondsPerDay = 1000 * 60 * 60 * 24;
	return Math.floor((utc2 - utc1) / millisecondsPerDay);
};

const todayUTC = () => {
	const now = new Date();
	return new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
};

export { getDaysDiff, todayUTC };
