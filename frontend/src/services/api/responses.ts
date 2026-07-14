import type { SuccessQuery } from "@/services/api/openapi";

/**
 * We tie the response types to the API schema in order to detect changes in the API as early as possible.
 */

type OptionalResponseHolding = SuccessQuery<"/api/v1/find-my-agricultural-holding">["holding"];
type ResponseHolding = OptionalResponseHolding extends null
	? never
	: Exclude<OptionalResponseHolding, null>;
type ResponseFarm = ResponseHolding extends null ? never : ResponseHolding["farms"][number];
type ResponseSection = ResponseFarm extends null ? never : ResponseFarm["sections"][number];

export type { ResponseFarm, ResponseHolding, ResponseSection };
