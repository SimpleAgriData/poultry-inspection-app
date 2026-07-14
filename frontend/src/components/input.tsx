import type React from "react";
import { useState } from "react";
import { IconContext } from "react-icons";
import { Subtitled } from "@/components/subtitled";

type TypePairs = {
	text: string;
	password: string;
	email: string;
	number: number | null;
	tel: string;
	date: Date | null;
	time: string;
};

type TypeOptions = {
	text: {
		maxLength: number;
	};
	date: {
		min: Date;
		max: Date;
	};
	number: {
		min: number;
		max: number;
		step: number;
	};
};

type InputType = keyof TypePairs;
type InputWithOptionsType = Extract<InputType, keyof TypeOptions>;

type InputMode = React.HTMLAttributes<HTMLInputElement>["inputMode"];

type Options<T extends InputType> = T extends keyof TypeOptions ? Partial<TypeOptions[T]> : never;

type ResolvedOptions = {
	maxLength?: number;
	min?: string | number;
	max?: string | number;
	step?: number;
};

type InputWithOptionsTypeResolvers = {
	[K in InputWithOptionsType]: (options: Options<K>) => ResolvedOptions;
};

type AnyInputTypeResolvers = {
	[K in InputType]?: (options: Options<K>) => ResolvedOptions;
};

const formatDate = (date: Date): string => {
	const year = date.getFullYear();
	const month = String(date.getMonth() + 1).padStart(2, "0");
	const day = String(date.getDate()).padStart(2, "0");
	return `${year}-${month}-${day}`;
};

const resolvers: AnyInputTypeResolvers = {
	date: (options) => ({
		min: options.min ? formatDate(options.min) : undefined,
		max: options.max ? formatDate(options.max) : undefined,
	}),
	text: (options) => options,
	number: (options) => options,
} satisfies InputWithOptionsTypeResolvers; // Using satisfies here to ensure we have resolvers for all InputWithOptionsType while being able to index with InputType in the main resolvers object

const resolveOptions = <T extends InputType>(type: T, options: Options<T>): ResolvedOptions => {
	const resolver = resolvers[type];
	if (!resolver) {
		return {};
	}
	return resolver(options);
};

interface IProps<T extends keyof TypePairs> {
	type: T;
	inputMode?: InputMode;
	value?: TypePairs[T] | null;
	onChange: (value: TypePairs[T]) => void;
	placeholder?: string;
	label?: string;
	iconLeft?: React.ReactNode;
	iconRight?: React.ReactNode;
	disabled?: boolean;
	description?: string;
	required?: boolean;
	options?: Options<T>;
}

function Input<K extends keyof TypePairs>(props: IProps<K>) {
	const [hadFocus, setHadFocus] = useState(false);

	const options = props.options ? resolveOptions(props.type, props.options) : {};

	const formatValue = (type: K, value: TypePairs[K] | null | undefined): string => {
		if (value === null || value === undefined) return "";
		switch (type) {
			case "date": {
				const date = value as Date;
				const year = date.getFullYear();
				const month = String(date.getMonth() + 1).padStart(2, "0");
				const day = String(date.getDate()).padStart(2, "0");
				return `${year}-${month}-${day}`;
			}
			case "number":
				return (value as number).toString();
			default:
				return value.toString();
		}
	};

	const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		switch (props.type) {
			case "number":
				if (e.target.value === "") {
					props.onChange(null as TypePairs[K]);
				} else {
					props.onChange(e.target.valueAsNumber as TypePairs[K]);
				}
				break;
			case "date":
				if (e.target.value === "") {
					props.onChange(null as TypePairs[K]);
				} else {
					props.onChange(e.target.valueAsDate as TypePairs[K]);
				}
				break;
			default:
				props.onChange(e.target.value as TypePairs[K]);
				break;
		}
	};

	const hasValue = () => {
		const value = props.value;
		if (value === null || value === undefined) return false;
		if (typeof value === "string") return value.trim() !== "";
		return true;
	};

	const onBlur = () => {
		if (!hadFocus) {
			setHadFocus(true);
		}
	};

	const errorStyles =
		props.required && hadFocus && !hasValue()
			? "border-error focus-within:border-red-500 focus-within:ring-error/30 ring-2 ring-error/30"
			: "border-outline focus-within:border-primary focus-within:ring-primary/30";

	return (
		<IconContext.Provider value={{ size: "1.5em" }}>
			{props.label && (
				<label
					htmlFor={`input-${props.label}`}
					className="block mb-2 text-base font-medium text-on-secondary-container"
				>
					{props.label}
				</label>
			)}
			<Subtitled subtitle={props.description}>
				<div
					onBlur={onBlur}
					className={`flex items-center bg-background text-on-secondary-container
					border outline-0 shadow-sm rounded-md w-full p-3 min-w-0
					focus-within:ring-2
					${errorStyles}
					${props.disabled ? `opacity-50 cursor-not-allowed` : ""}
					`}
				>
					{props.iconLeft && <div className="inline-block mr-2">{props.iconLeft}</div>}
					<input
						step={options.step}
						min={options.min}
						max={options.max}
						maxLength={options.maxLength}
						id={`input-${props.label}`}
						type={props.type}
						inputMode={props.inputMode}
						value={formatValue(props.type, props.value)}
						disabled={props.disabled}
						onChange={onChange}
						placeholder={props.placeholder}
						className={`w-full min-w-0 text-sm bg-background outline-0 outline-outline border-0
					placeholder:font-medium text-on-surface
							${props.disabled ? "cursor-not-allowed" : ""}`}
					/>
					{props.iconRight && <div className="inline-block ml-2">{props.iconRight}</div>}
				</div>
			</Subtitled>
		</IconContext.Provider>
	);
}

export default Input;
