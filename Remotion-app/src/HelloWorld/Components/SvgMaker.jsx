import React, {useCallback, useEffect, useState} from 'react';

import {continueRender, delayRender} from 'remotion';
import GsapAnimation from './GsapAnimation';
import gsap from 'gsap';
export default function SvgMaker(props) {
	const [svgData, setSvgPath] = useState(null);

	const [handle] = useState(() => delayRender());

	const fetchData = useCallback(async () => {
		try {
			const response = await fetch(
				'https://yakova-svg.hf.space/generateSVGPath',
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						text: props.text,
						size: 150,
						separate: true,
						strokeWidth:props.strokeWidth,
						fill: props.fill,
						individualLetters: true,
						stroke: 'black',
						fontUrl:
							'https://bla-tranny.hf.space/stream/?id=131',
					}),
				}
			);

			if (!response.ok) {
				throw new Error('Network response was not ok');
			}

			const data = await response.json();
			setSvgPath(data);
			continueRender(handle);
		} catch (error) {
			console.error('Error fetching data:', error);
		}
	}, []);

	useEffect(() => {
		fetchData();
	}, []);

	return (
		<div  className="absolute  flex">
			{svgData &&
				Array.from(props.text).map((key) => {
					const {style, ...otherAttributes} = svgData[key].svg.g.$;
					return (
						<>
							<div className={props.className}		id={`${props.id}`}  style={props.style}>
								<svg
									key={`${props.id}`}
									xmlns="http://www.w3.org/2000/svg"
									style={
										{
											// transformStyle: 'preserve-3d',
											// transform:'translateZ(0px)'
										}
									}
									// transform="perspective(200) rotateX(45)"
									{...svgData[key].svg.$} // Set SVG attributes from JSON
								>
									<g {...otherAttributes}>
										<path {...svgData[key].svg.g.path.$} />
									</g>
								</svg>
							</div>
						</>
					);
				})}
		</div>
	);
}

export const SVG3D = ({text}) => {
	return (
		<GsapAnimation Timeline={Timeline}>
			<SvgMaker
				text={text}
				style={{transformStyle: 'preserve-3d', transform:'translateY(100%)',backgroundColor:'transparent'}}
				id="svg1"
				fill="yellow"
				className=""

			/>
			<SvgMaker
				text={text}
				style={{transformStyle: 'preserve-3d', transform:'translateY(100%)',backgroundColor:'transparent'}}
				id="svg2"
				fill="white"
				className="opacity-0"
			/>
		</GsapAnimation>
	);
};


const Timeline = () => {
let timeline=gsap.timeline()
//constants
let duration = 0.8; // Duration of each animation step
let stagger = { each: 0.02, ease: "power2", from: "start" }; // Stagger settings
const ease = "slow"; // Ease for all animations

timeline.set('#svg2',{rotationX:-90,opacity:0,transformOrigin:"50% 50% -100",ease:"power4.in"})


timeline.to('#svg2', {duration:duration, opacity:1, stagger:stagger}, 0.001)



timeline.to('#svg2',{rotationX:0,duration:duration,stagger:stagger,ease:ease},0)



timeline.to('#svg1',{rotationX:90,duration:duration, stagger:stagger,transformOrigin:
	"50% 50% -100",opacity:0,ease:ease},0)
	return timeline
}