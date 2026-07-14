import type React from "react";

interface PageLayoutProps {
	children: React.ReactNode;
	className?: string;
}

/**
 * The default page layout component with preset padding and max width.
 * @param children
 * @param className
 * @constructor
 */
export function PageLayout({ children, className }: PageLayoutProps) {
	return (
		<div className="h-full flex justify-center overflow-y-auto gutter-stable">
			<div className={"w-full min-h-0 flex-1 max-w-md p-4 flex flex-col"}>
				<div className={`flex-1 ${className ?? ""}`}>{children}</div>
				<div className="w-full max-w-md mx-auto text-center text-on-surface-variant text-xs py-4">
					&copy; {new Date().getFullYear()} SimpleAgriData
				</div>
			</div>
		</div>
	);
}
