"use client";

import { useEffect, useState } from "react";

export default function Ellipsis({
	delayMs,
	fixedWidth,
}: {
	delayMs: number;
	fixedWidth?: boolean;
}) {
	const [dots, setDots] = useState(1);

	useEffect(() => {
		const interval = setInterval(() => {
			setDots((prevDots) => (prevDots % 3) + 1);
		}, delayMs);

		return () => clearInterval(interval);
	}, [delayMs]);

	return (
		<span className={fixedWidth ? "w-[1em] inline-block text-left" : ""}>{".".repeat(dots)}</span>
	);
}
