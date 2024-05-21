import {Series} from 'remotion';
import React from 'react';
import {staticFile, useVideoConfig, Audio} from 'remotion';
import sfxSequences from './Assets/SfxSequences.json';
import {TransitionSeries} from '@remotion/transitions';
const SfxStream = React.memo(() => {
	const {fps} = useVideoConfig();
	return (
		<TransitionSeries>
			{sfxSequences.map((entry, index) => {
				return (
					<TransitionSeries.Sequence
						key={index}
						from={fps * entry.start}
						durationInFrames={30}
					>
						<Audio
							volume={entry.props.volume}
							startFrom={entry.props.startFrom}
							src={staticFile(entry.name)}
						/>
					</TransitionSeries.Sequence>
				);
			})}
		</TransitionSeries>
	);
});

export default SfxStream;
