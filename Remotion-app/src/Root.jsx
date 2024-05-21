import {Composition} from 'remotion';
import Constants from './HelloWorld/Assets/Constants.json';
import './index.css';
import HelloWorld from './HelloWorld';
export const RemotionRoot = () => {
	return (
		<>
			<Composition
				id="HelloWorld"
				component={HelloWorld}
				durationInFrames={Constants?.duration ? Constants.duration : 60 * 30}
				fps={30}
				height={Constants?.height ? Constants.height : 1920}
				width={Constants?.width ? Constants.width : 1080}
			/>
		</>
	);
};
