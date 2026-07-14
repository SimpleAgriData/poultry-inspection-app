import { usePathname } from "next/dist/client/components/navigation";
import Link from "next/link";
import type React from "react";
import { IconContext } from "react-icons";

export interface NavigationBarItem {
	label: string;
	href: string;
	icon: React.ReactNode;
	iconActive?: React.ReactNode;
}

interface NavigationBarProps {
	items: NavigationBarItem[];
	onNavigate?: (index: number) => void;
}

function Item({
	item,
	isActive,
	onClick,
}: {
	item: NavigationBarItem;
	isActive: boolean;
	onClick: () => void;
}) {
	return (
		<div
			className={`flex flex-col items-center justify-center flex-1 text-sm transition-colors duration-200
							${isActive ? "text-primary" : "text-on-surface-variant"}`}
		>
			<Link key={item.label} href={item.href} onClick={onClick} className={"group"}>
				<IconContext.Provider value={{ size: "1.5em" }}>
					<div className={`relative px-4 py-0.5 rounded-full flex justify-center mx-auto w-fit`}>
						<div
							className={`absolute w-0 h-full top-0 mx-auto rounded-full transition-all
							${
								isActive
									? "w-full text-on-secondary-container bg-secondary-container"
									: "group-active:w-full group-active:bg-surface-container-high"
							}
							`}
						></div>
						<div className="relative ">
							{isActive && item.iconActive ? item.iconActive : item.icon}
						</div>
					</div>
				</IconContext.Provider>
				<span className={`text-xs ${isActive ? "font-semibold" : ""}`}>{item.label}</span>
			</Link>
		</div>
	);
}

export function NavigationBar({ items, onNavigate }: NavigationBarProps) {
	const currentPath = usePathname();
	const isActivePath = (href: string) => href === currentPath;

	return (
		<nav className="bottom-0 left-0 right-0 bg-surface-container-low shadow-black shadow-lg">
			<div className="flex justify-around h-16">
				{items.map((item, index) => (
					<Item
						key={item.label}
						item={item}
						isActive={isActivePath(item.href)}
						onClick={() => onNavigate?.(index)}
					/>
				))}
			</div>
		</nav>
	);
}
