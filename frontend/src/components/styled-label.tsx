import type React from "react";

export type StyledLabelType = "primary" | "secondary" | "tertiary" | "warning" | "error";

const styles: Record<StyledLabelType, string> = {
	primary: "text-on-primary-container bg-primary-container border-primary",
	secondary: "text-on-secondary-container bg-secondary-container border-secondary",
	tertiary: "text-on-tertiary-container bg-tertiary-container border-tertiary",
	warning: "text-on-warning-container bg-warning-container border-warning",
	error: "text-on-error-container bg-error-container border-error",
};

interface StyledLabelProps {
	type: StyledLabelType;
	children?: React.ReactNode;
	className?: string;
	icon?: React.ReactNode;
}

export function StyledLabel({ type, children, icon, className }: StyledLabelProps) {
	const style = styles[type] || styles.primary;
	return (
		<div className={className}>
			<div
				className={`flex flex-row items-center gap-2 text-sm border px-2 py-0.5 rounded-md font-body ${style}`}
			>
				{icon}
				<span>{children}</span>
			</div>
		</div>
	);
}
