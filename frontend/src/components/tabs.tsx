import type React from "react";
import { useLayoutEffect, useRef, useState } from "react";
import { MdKeyboardArrowLeft, MdKeyboardArrowRight } from "react-icons/md";
import styles from "./tabs.module.css";

export interface TabItem {
	title: string;
	icon?: React.ReactNode;
}

interface TabsProps {
	tabs: TabItem[];
	activeTabIndex: number;
	onTabChange: (index: number) => void;
	align?: "left" | "center";
}

interface TabItemRect {
	left: number;
	width: number;
}

const isIndexFullyVisible = (container: HTMLElement, index: number) => {
	const items = container.children;
	if (index < 0 || index >= items.length) return false;

	const item = items[index];
	const itemRect = item.getBoundingClientRect();
	const containerRect = container.getBoundingClientRect();

	return itemRect.left >= containerRect.left && itemRect.right <= containerRect.right;
};

const findLastFullyVisibleItemIndex = (container: HTMLElement) => {
	const items = container.children;
	for (let i = items.length - 1; i >= 0; i--) {
		const isFullyVisible = isIndexFullyVisible(container, i);
		if (isFullyVisible) {
			return i;
		}
	}
	return -1;
};

const findFirstFullyVisibleItemIndex = (container: HTMLElement) => {
	const items = container.children;
	for (let i = 0; i < items.length; i++) {
		const isFullyVisible = isIndexFullyVisible(container, i);
		if (isFullyVisible) {
			return i;
		}
	}
	return -1;
};

const useIsOverflowing = <T extends HTMLElement>() => {
	const ref = useRef<T>(null);
	const [isOverflowing, setIsOverflowing] = useState(false);

	useLayoutEffect(() => {
		const element = ref.current;
		if (!element) return;

		const checkOverflow = () => {
			const hasOverflow = element.scrollWidth > element.clientWidth;

			// Only update state if the value has actually changed
			setIsOverflowing((prev) => {
				if (prev !== hasOverflow) return hasOverflow;
				return prev;
			});
		};

		checkOverflow();

		const observer = new ResizeObserver(checkOverflow);
		observer.observe(element);

		return () => observer.disconnect();
	}, []);

	return { ref, isOverflowing };
};

export default function Tabs(props: TabsProps) {
	const isActiveTab = (index: number) => index === props.activeTabIndex;
	const { ref: scrollContainerRef, isOverflowing } = useIsOverflowing<HTMLDivElement>();
	const tabsContainerRef = useRef<HTMLDivElement>(null);
	const [activeTabRect, setActiveTabRect] = useState<TabItemRect | null>(null);

	useLayoutEffect(() => {
		const tabsContainer = tabsContainerRef.current;
		if (!tabsContainer) return;

		const activeTabElement = tabsContainer.children[props.activeTabIndex];
		if (!activeTabElement) return;

		const itemRect = activeTabElement.getBoundingClientRect();
		const tabsContainerRect = tabsContainer.getBoundingClientRect();

		setActiveTabRect({
			left: itemRect.left - tabsContainerRect.left,
			width: itemRect.width,
		});
	}, [props.activeTabIndex]);

	const onClickTab = (index: number) => {
		props.onTabChange(index);
		const tabsContainer = tabsContainerRef.current;
		const scrollContainer = scrollContainerRef.current;
		if (!tabsContainer || !scrollContainer) return;

		const tabElements = tabsContainer.children;

		if (index < 0 || index >= tabElements.length) return;

		const tabElement = tabElements[index];
		const tabRect = tabElement.getBoundingClientRect();
		const containerRect = scrollContainer.getBoundingClientRect();

		const extraScroll = 40;

		if (tabRect.left < containerRect.left) {
			scrollContainer.scrollBy({
				left: tabRect.left - containerRect.left - extraScroll,
				behavior: "smooth",
			});
		} else if (tabRect.right > containerRect.right) {
			scrollContainer.scrollBy({
				left: tabRect.right - containerRect.right + extraScroll,
				behavior: "smooth",
			});
		}
	};

	const onScrollButtonClick = (direction: "left" | "right") => {
		const scrollContainer = scrollContainerRef.current;
		if (!scrollContainer) return;

		const tabsContainer = tabsContainerRef.current;
		if (!tabsContainer) return;

		const items = tabsContainer.children;
		if (items.length === 0) return;

		let scrollAmount = 150; //default scroll amount
		if (direction === "left") {
			const firstFullyVisibleIndex = findFirstFullyVisibleItemIndex(tabsContainer);
			if (firstFullyVisibleIndex > 0) {
				const firstFullyVisibleItem = items[firstFullyVisibleIndex];
				const itemRect = firstFullyVisibleItem.getBoundingClientRect();
				const containerRect = tabsContainer.getBoundingClientRect();

				const itemOffset = containerRect.right - itemRect.right;

				scrollAmount = itemOffset + itemRect.width / 2;
			}
		} else {
			const lastFullyVisibleIndex = findLastFullyVisibleItemIndex(tabsContainer);
			if (lastFullyVisibleIndex >= 0 && lastFullyVisibleIndex < items.length - 1) {
				const lastFullyVisibleItem = items[lastFullyVisibleIndex];
				const itemRect = lastFullyVisibleItem.getBoundingClientRect();
				const containerRect = tabsContainer.getBoundingClientRect();

				const itemOffset = itemRect.left - containerRect.left;

				scrollAmount = itemOffset + itemRect.width / 2;
			}
		}

		scrollAmount = Math.max(scrollAmount, 50); //minimum scroll amount

		const scrollOptions: ScrollToOptions = {
			left: direction === "left" ? -scrollAmount : scrollAmount,
			behavior: "smooth",
		};
		scrollContainer.scrollBy(scrollOptions);
	};

	const renderScrollButton = (direction: "left" | "right") => {
		const iconSize = "1.5em";
		const icon =
			direction === "left" ? (
				<MdKeyboardArrowLeft size={iconSize} />
			) : (
				<MdKeyboardArrowRight size={iconSize} />
			);
		return (
			<button
				type="button"
				onClick={() => onScrollButtonClick(direction)}
				className={`shrink-0 p-2 cursor-pointer rounded-full`}
			>
				{icon}
			</button>
		);
	};

	const renderTabs = () => {
		return (
			<div
				className={`flex-1 overflow-x-auto no-scrollbar ${styles["scroll-transparency-wrapper"]}`}
				ref={scrollContainerRef}
			>
				<div
					className={`flex flex-row relative gap-2 ${props.align === "center" ? "justify-center-safe" : "justify-start"}`}
					ref={tabsContainerRef}
				>
					{props.tabs.map((tab, index) => (
						// biome-ignore lint/suspicious/noArrayIndexKey: index as key is acceptable here since tabs are static and won't change order
						<div className="flex flex-col items-center" key={index}>
							<button
								onClick={() => onClickTab(index)}
								className={`px-2 py-2 whitespace-nowrap font-medium cursor-pointer flex flex-row items-center gap-2 ${
									isActiveTab(index) ? "text-primary" : "text-on-surface-variant"
								}`}
							>
								{tab.icon && <span className="text-lg">{tab.icon}</span>}
								{tab.title}
							</button>
						</div>
					))}
					{activeTabRect && (
						<div
							className={
								"absolute bottom-0 h-1 w-3 transition-all bg-primary rounded-t-md translate-x-[-50%]"
							}
							style={{
								left: activeTabRect.left + activeTabRect.width / 2,
								width: activeTabRect.width / 2,
							}}
						></div>
					)}
				</div>
			</div>
		);
	};

	return (
		<div className={"flex flex-row items-center border-b border-on-surface-variant"}>
			{isOverflowing && renderScrollButton("left")}
			{renderTabs()}
			{isOverflowing && renderScrollButton("right")}
		</div>
	);
}
