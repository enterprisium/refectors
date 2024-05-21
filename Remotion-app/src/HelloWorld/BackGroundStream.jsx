import React from 'react';
import {staticFile, useVideoConfig, Audio} from 'remotion';
import backgroundSequences from './Assets/BackgroundSequences.json';
import {TransitionSeries} from '@remotion/transitions';

const BackgroundStream = React.memo(() => {
	const {fps} = useVideoConfig();
	return (
		<TransitionSeries
			style={{
				color: 'white',
				position: 'absolute',
				zIndex: 0,
			}}
		>
			{backgroundSequences.map((entry, index) => {
				return (
					<TransitionSeries.Sequence
						key={index}
						from={fps * entry.start}
						durationInFrames={fps * (entry.end - entry.start)}
					>
						<Audio
							volume={entry.props.volume}
							endAt={entry.props.endAt}
							startFrom={entry.props.startFrom}
							src={staticFile(entry.name)}
						/>
					</TransitionSeries.Sequence>
				);
			})}
		</TransitionSeries>
	);
});

export default BackgroundStream;
