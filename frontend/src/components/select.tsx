"use client";

import { useEffect, useRef, useState } from "react";
import { MdKeyboardArrowDown } from "react-icons/md";
import { Subtitled } from "@/components/subtitled";
import { useBackdrop } from "@/contexts/BackdropOverlay";

type Primitive = string | number;

export interface SelectOption<T extends Primitive> {
	value: T;
	label: string;
}

interface SelectProps<T extends Primitive> {
	value: T | null;
	onChange: (value: T | null) => void;
	options: SelectOption<T>[];
	allowClear?: boolean;
	placeholder?: string;
	label?: string;
	disabled?: boolean;
	required?: boolean;
	description?: string;
}

function Select<T extends Primitive>({
	value,
	onChange,
	options,
	allowClear,
	placeholder = "Bitte auswählen",
	label,
	disabled,
	required,
	description,
}: SelectProps<T>) {
	const { setBackdrop, clearBackdrop } = useBackdrop();
	const [isOpen, setIsOpen] = useState(false);
	const [hadFocus, setHadFocus] = useState(false);
	const selectRef = useRef<HTMLDivElement>(null);

	const selectedOption = options.find((opt) => opt.value === value);

	useEffect(() => {
		const handleClickOutside = (event: MouseEvent) => {
			if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
				setIsOpen(false);
			}
		};

		document.addEventListener("mousedown", handleClickOutside);
		return () => document.removeEventListener("mousedown", handleClickOutside);
	}, []);

	const handleSelect = (optionValue: T | null) => {
		onChange(optionValue);
		setIsOpen(false);
	};

	const onToggleOpen = () => {
		if (disabled) return;
		const newState = !isOpen;

		if (!newState) {
			setHadFocus(true);
		}

		setIsOpen(newState);
	};

	useEffect(() => {
		if (isOpen) {
			setBackdrop({ blur: "2px", color: "rgba(20,20,20,0.1)" });
		} else {
			clearBackdrop();
		}
	}, [setBackdrop, clearBackdrop, isOpen]);

	const onBlur = () => {
		if (!hadFocus) {
			setHadFocus(true);
		}
	};

	const hasError = required && hadFocus && !selectedOption;
	const errorStyles =
		hasError && !isOpen
			? "border-error focus-within:border-red-500 focus-within:ring-error/30 ring-2 ring-error/30"
			: "border-outline focus-within:border-primary focus-within:ring-primary/30";

	return (
		<div className="flex flex-col w-full" ref={selectRef} onBlur={onBlur}>
			{label && (
				<span className={`font-medium text-on-secondary-container text-base mb-2`}>{label}</span>
			)}
			<div className={`relative ${isOpen ? "z-10" : ""}`}>
				<Subtitled subtitle={description}>
					<button
						type="button"
						onClick={onToggleOpen}
						disabled={disabled}
						className={`flex items-center justify-between w-full p-3 bg-background border rounded-md shadow-sm
					focus-within:ring-2
						${errorStyles}
						${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:border-on-surface-variant"}`}
					>
						<span
							className={`text-sm font-medium ${selectedOption ? "text-on-surface" : "text-outline"}`}
						>
							{selectedOption?.label || placeholder}
						</span>
						<MdKeyboardArrowDown
							className={`size-6 text-on-surface transition-transform ${isOpen ? "rotate-180" : ""}`}
						/>
					</button>
				</Subtitled>

				{isOpen && (
					<div className="absolute z-50 w-full mt-1 bg-background border border-outline rounded-md shadow-lg max-h-60 overflow-y-auto">
						{options.length === 0 ? (
							<div className="px-3 py-3 text-sm text-outline">Keine Optionen verfügbar</div>
						) : (
							<>
								{options.map((option) => (
									<button
										key={option.value}
										type="button"
										onClick={() => handleSelect(option.value)}
										className={`w-full px-3 py-3 text-left text-sm hover:bg-surface-variant transition-colors cursor-pointer
										${option.value === value ? "bg-surface-variant text-primary font-medium" : "text-on-surface"}`}
									>
										{option.label}
									</button>
								))}
								{allowClear && value !== null && (
									<>
										<hr className="my-1 border-outline" />
										<button
											type="button"
											onClick={() => handleSelect(null)}
											className="w-full px-3 py-3 text-left text-sm text-error hover:bg-surface-variant transition-colors cursor-pointer"
										>
											Löschen
										</button>
									</>
								)}
							</>
						)}
					</div>
				)}
			</div>
		</div>
	);
}

export default Select;
