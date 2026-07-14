import type React from "react";
import { IconContext } from "react-icons";
import { MdErrorOutline, MdInfoOutline, MdWarning } from "react-icons/md";

type InfoBannerType = "info" | "warning" | "error";

const styles: Record<InfoBannerType, string> = {
	info: "text-on-secondary-container bg-secondary-container/50 border-primary",
	warning: "text-on-warning-container bg-warning-container border-warning",
	error: "text-on-error-container bg-error-container border-error",
};

const defaultIcons: Record<InfoBannerType, React.ReactNode> = {
	info: <MdInfoOutline />,
	warning: <MdWarning />,
	error: <MdErrorOutline />,
};

interface InfoBannerProps {
	icon: React.ReactNode | "auto";
	type: InfoBannerType;
	align?: "left" | "center" | "right";
}

export function InfoBanner({
	icon,
	type,
	align = "left",
	children,
}: React.PropsWithChildren<InfoBannerProps>) {
	const style = styles[type] || styles.info;
	const resolvedIcon = icon === "auto" ? defaultIcons[type] : icon;

	const alignmentClasses = {
		left: "justify-start text-left",
		center: "justify-center text-center",
		right: "justify-end text-right",
	};

	return (
		<div
			className={`border rounded-md p-3 text-sm flex items-center gap-3 mt-2 ${style} ${alignmentClasses[align]}`}
		>
			<IconContext.Provider value={{ className: "shrink-0", size: "2em" }}>
				{resolvedIcon}
			</IconContext.Provider>
			{children}
		</div>
	);
}
