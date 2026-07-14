import type React from "react";

interface PageSectionProps {
	title: React.ReactNode;
	titleIcon?: React.ReactNode;
	children: React.ReactNode;
	noBodyStyle?: boolean;
}

export default function PageSection({ title, titleIcon, children, noBodyStyle }: PageSectionProps) {
	return (
		<div className="flex flex-col w-full gap-2">
			<h2 className="text-primary text-lg font-medium flex items-center gap-2 w-full">
				{titleIcon}
				{title}
			</h2>
			{noBodyStyle ? (
				children
			) : (
				<div className="bg-surface rounded-xl shadow-lg p-6 space-y-6">{children}</div>
			)}
		</div>
	);
}
