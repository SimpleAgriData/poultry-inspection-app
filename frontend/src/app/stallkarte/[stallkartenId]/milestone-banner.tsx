import { MdInfoOutline } from "react-icons/md";
import { InfoBanner } from "@/components/info-banner";
import type { Milestone } from "@/services/domain/milestones";

export function MilestoneBanner({ milestone }: { milestone: Milestone }) {
	return (
		<InfoBanner icon={<MdInfoOutline />} type={"warning"}>
			{milestone.description}
		</InfoBanner>
	);
}
