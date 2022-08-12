import { getAddress } from '@ethersproject/address';
import { BigNumber } from '@ethersproject/bignumber';


export const toAddress = bn => {
	try {
		return getAddress(BigNumber.from(bn).toHexString());
	} catch (e) {
		return bn;
	}
};

export const dateFormat = timestamp => {
	const date = new Date(timestamp * 1000);
	
	const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
	const month = months[date.getUTCMonth()];
	const day = date.getUTCDate();
	const year = date.getUTCFullYear();
	const hour = date.getUTCHours();
	const minute = date.getUTCMinutes();
	const second = date.getUTCSeconds();

	return {
			fullDay: `${year}-${month}-${day}`,
			time: `${hour}:${minute}:${second}`
	};
};

export const checkpointSourceBridge = (address: string, startingBlock: number) => {
	return {
		contract: address,
		start: startingBlock,
		events: [
			{
				name: "deposit_handled",
				fn: "handleDeposit"
			},
			{
				name: "withdraw_initiated",
				fn: "handleWithdraw"
			},
			{
				name: "force_withdrawal_handled",
				fn: "handleWithdraw"
			}
		]
	};
}

export const checkpointSourceTransfer = (address: string, startingBlock: number) => {
	return {
		contract: address,
		start: startingBlock,
		events: [
			{
				name: "Transfer",
				fn: "handleTransfer"
			}
		]
	}
}