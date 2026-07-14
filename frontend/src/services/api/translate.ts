import type { ResponseFarm, ResponseHolding, ResponseSection } from "@/services/api/responses";
import type { Farm, Holding, Section } from "@/services/domain/holding";

const responseSectionToDomain = (response: ResponseSection): Section => ({
	id: response.id,
	name: response.name,
});

const responseFarmToDomain = (response: ResponseFarm): Farm => ({
	id: response.id,
	name: response.name,
	type: response.type,
	vvvoNumber: response.vvvo_number,
	sections: response.sections.map(responseSectionToDomain),
});

const responseHoldingToDomain = (response: ResponseHolding): Holding => {
	return {
		id: response.id,
		name: response.name,
		ownerUserId: response.owner_user_id,
		breed: response.breed,
		hatchery: response.hatchery,
		ecoControlNumber: response.eco_control_number,
		addressStreet: response.address_street,
		addressZip: response.address_zip,
		addressCity: response.address_city,
		farms: response.farms.map(responseFarmToDomain),
	};
};

export { responseFarmToDomain, responseHoldingToDomain, responseSectionToDomain };
