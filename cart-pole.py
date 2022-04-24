import gym
import logging
from signal import samplePoint, Signal, Sample


logging.basicConfig(level=logging.DEBUG)

def theta_omega_policy(obs):
	theta, w = obs[2:4]
	if abs(theta) < 0.03:
		return 0 if w < 0 else 1
	else:
		return 0 if theta < 0 else 1



# env = gym.make('CartPole-v1')
# for i_episode in range(20):
# 	print(i_episode)
# 	observation = env.reset()
# 	for t in range(100):
# 		env.render()
# 		#print(observation)
# 		#action = env.action_space.sample()
# 		action = theta_omega_policy(observation)
# 		observation, reward, done, info = env.step(action)
# 		print(observation, reward, done, info)
# 		if done:
# 			print("Episode finished after {} timesteps".format(t+1))
# 			break
# env.close()


def generateSignals(signalfile = 'cart-pole.signal', pos_number=5, neg_number=5, T=10):
	
	env = gym.make('CartPole-v1')
	sample = Sample()


	#generate positive examples
	i=0
	while i < pos_number:

		
		observation = env.reset()
		signal = Signal(sequence=[])
		for t in range(T):
			
			env.render()
			action = theta_omega_policy(observation)
			observation, reward, fail, info = env.step(action)
			sp = samplePoint(time=t, vector=list(observation))
			signal.addPoint(sp)
			
			if fail:
				#print("Episode finished after {} timesteps".format(t+1))
				break
		
		if not fail:
			sample.positive.append(signal)
			logging.info("Generating positive word %d"%i)
			i+=1

	#generate negative examples
	i=0
	while i < neg_number:
		signal = Signal(sequence=[])
		observation = env.reset()
		for t in range(T):

			env.render()
			action = env.action_space.sample()
			observation, reward, fail, info = env.step(action)
			sp = samplePoint(time=t, vector=list(observation))
			signal.addPoint(sp)

			if fail:
				sample.negative.append(signal)
				logging.info("Generating negative word %d"%i)
				i+=1
				#print("Episode finished after {} timesteps".format(t+1))
				break


	sample.vars = ['x', 'v', 't', 'o']
	### change the predicates here ###
	sample.predicates = {'x': [0.2,0.3], 'v':[], 't':[], 'o':[0.5,0.7]}
	sample.writeSample(signalfile)


generateSignals()
				

				




