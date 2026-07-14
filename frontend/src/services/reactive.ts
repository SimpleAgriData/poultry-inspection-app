type Unsubscribe = () => void;
type Subscriber<T> = (value: T) => void;

interface ReadOnlyObservable<T> {
	readonly value: T;
	next(): Promise<T>;
	subscribe(subscriber: Subscriber<T>, includeCurrentValue: boolean): Unsubscribe;
	unsubscribe(subscriber: Subscriber<T>): void;
}

interface ReadWriteObservable<T> extends ReadOnlyObservable<T> {
	set(value: T): void;
}

interface ObservableOptions {
	notifyOnEqualValue: boolean;
}

/**
 * A simple observable implementation that allows subscribers to listen for changes to a value.
 */
class Observable<T> implements ReadWriteObservable<T> {
	protected observableValue: T;
	protected subscribers: Subscriber<T>[] = [];
	protected readonly notifyOnEqualValue: boolean;

	constructor(initialValue: T, { notifyOnEqualValue }: Partial<ObservableOptions> = {}) {
		this.notifyOnEqualValue = notifyOnEqualValue ?? false;
		this.observableValue = initialValue;
	}

	#notifySubscribers() {
		for (const subscriber of this.subscribers) {
			subscriber(this.observableValue);
		}
	}

	get value() {
		return this.observableValue;
	}

	set value(value: T) {
		this.set(value);
	}

	set(value: T) {
		if (this.observableValue === value && !this.notifyOnEqualValue) {
			return;
		}

		this.observableValue = value;
		this.#notifySubscribers();
	}

	next(): Promise<T> {
		return new Promise((resolve) => {
			const unsubscribe = this.subscribe((value) => {
				resolve(value);
				unsubscribe();
			}, false);
		});
	}

	subscribe(subscriber: Subscriber<T>, includeCurrentValue: boolean): Unsubscribe {
		this.subscribers.push(subscriber);

		if (includeCurrentValue) {
			subscriber(this.observableValue);
		}

		return () => this.unsubscribe(subscriber);
	}

	unsubscribe(subscriber: Subscriber<T>) {
		this.subscribers = this.subscribers.filter((s) => s !== subscriber);
	}

	disconnect() {
		for (const subscriber of this.subscribers) {
			this.unsubscribe(subscriber);
		}
	}
}

interface ReadOnlyNotifier<T> extends ReadOnlyObservable<T> {}
interface ReadWriteNotifier<T> extends ReadOnlyNotifier<T> {
	notify(value: T): void;
}

class Notifier<T> extends Observable<T> implements ReadWriteNotifier<T> {
	constructor(initialValue: T) {
		super(initialValue, { notifyOnEqualValue: true });
	}

	notify(value: T) {
		this.set(value);
	}
}

export {
	Notifier,
	Observable,
	type ReadOnlyNotifier,
	type ReadOnlyObservable,
	type ReadWriteNotifier,
	type ReadWriteObservable,
	type Subscriber,
	type Unsubscribe,
};
