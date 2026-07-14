import type React from "react";

interface SubtitledProps {
	subtitle?: React.ReactNode;
	children: React.ReactNode;
}

export function Subtitled({ subtitle, children }: SubtitledProps) {
	return (
		<div className={"flex flex-col gap-2"}>
			{children}
			{subtitle && <p className={"text-xs text-on-secondary-container"}>{subtitle}</p>}
		</div>
	);
}
