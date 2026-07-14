import Link from "next/link";
import type React from "react";
import { useState } from "react";
import { IconContext } from "react-icons";
import { Spinner } from "@/components/spinner";

const defaultLayoutClasses = "flex items-center justify-center px-6 py-2";

const typeClasses = {
	primary: {
		theme: "bg-primary text-on-primary shadow-lg",
		layout: defaultLayoutClasses,
	},
	secondary: {
		theme: "bg-secondary text-on-secondary shadow-lg",
		layout: defaultLayoutClasses,
	},
	outline: {
		theme:
			"bg-transparent border border-outline text-on-surface shadow-lg hover:bg-surface-variant active:bg-surface ",
		layout: defaultLayoutClasses,
	},
	tertiary: {
		theme: "bg-tertiary text-on-tertiary shadow-lg",
		layout: defaultLayoutClasses,
	},
	warning: {
		theme: "bg-warning text-on-warning shadow-lg ",
		layout: defaultLayoutClasses,
	},
	danger: {
		theme: "bg-danger text-on-danger shadow-lg",
		layout: defaultLayoutClasses,
	},
	"danger-link": {
		theme: "bg-transparent text-danger hover:text-danger/80 active:text-danger/60",
		layout: "flex items-center justify-center py-2",
	},
	link: {
		theme: "bg-transparent text-primary hover:text-primary/80 active:text-primary/60",
		layout: "flex items-center justify-center py-2",
	},
} as const;

type Type = keyof typeof typeClasses;

type Width = "auto" | "full";

type ClickBehavior = "default" | "single-click";

interface IProps {
	withLoader?: boolean;
	type: Type;
	onClick?: () => void;
	href?: string;
	children: React.ReactNode;
	disabled?: boolean;
	width?: Width;
	iconLeft?: React.ReactNode;
	iconRight?: React.ReactNode;
	iconSize?: string;
	loaderOnClick?: boolean;
	loaderPosition?: "left" | "right";
	clickBehavior?: ClickBehavior;
	className?: string;
}

function Button(props: IProps) {
	const [clicked, setClicked] = useState(false);
	const onClickHandler = () => {
		if (props.clickBehavior === "single-click" && clicked) {
			return;
		}

		if (props.loaderOnClick && !props.disabled) {
			setClicked(true);
		}
		if (props.onClick) {
			props.onClick();
		}
	};

	const loaderEnabled = (props.loaderOnClick && clicked && !props.disabled) || props.withLoader;
	const showLoaderLeft = loaderEnabled && props.loaderPosition !== "right";
	const showLoaderRight = loaderEnabled && props.loaderPosition === "right";

	const leftIcon = showLoaderLeft ? <Spinner /> : props.iconLeft;
	const rightIcon = showLoaderRight ? <Spinner /> : props.iconRight;
	const iconSize = props.iconSize ?? "1.25em";

	const disabledTheme = props.disabled ? "opacity-50" : "";
	const widthClass = props.width === "auto" ? "w-auto" : "w-full";
	const wrapperTheme = `${typeClasses[props.type].theme} ${disabledTheme} ${widthClass} rounded-md`;

	const disabledLayout = props.disabled
		? "cursor-not-allowed"
		: "hover:cursor-pointer hover:brightness-90 active:brightness-75";
	const layout = `${typeClasses[props.type].layout} ${widthClass} ${disabledLayout}`;

	const renderContent = () => {
		return (
			<>
				{leftIcon && <span className="inline-block mr-2 shrink-0">{leftIcon}</span>}
				<span className={"font-medium"}>{props.children}</span>
				{rightIcon && <span className="inline-block ml-2 shrink-0">{rightIcon}</span>}
			</>
		);
	};

	return (
		<IconContext.Provider value={{ size: iconSize }}>
			{/* The Link component inherits some properties, thus overwriting the type specific classes */}
			{/* Therefor, we apply them in a wrapper.*/}
			<div className={`${wrapperTheme} ${props.className ?? ""}`}>
				{props.href ? (
					<Link
						className={layout}
						href={props.href}
						aria-disabled={props.disabled}
						onClick={onClickHandler}
					>
						{renderContent()}
					</Link>
				) : (
					<button
						type="button"
						className={layout}
						onClick={onClickHandler}
						disabled={props.disabled}
					>
						{renderContent()}
					</button>
				)}
			</div>
		</IconContext.Provider>
	);
}

export default Button;
