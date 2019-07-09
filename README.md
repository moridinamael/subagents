# Complex Behavior from Simple (Sub)Agents

---

### Context

The full context and purpose of this application can be found [here](https://www.lesswrong.com/posts/3pKXC62C98EgCeZc4/complex-behavior-from-simple-sub-agents) on LessWrong.com.

Take a simple agent, with no capacity for learning, that exists
on a 2D plane. It shares the plane with other agents and objects, to be described shortly.

The agent intrinsically doesn't want anything. But it can be assigned goal-like objects, which one might view as subagents. Each individual goal-like subagent can possess a simple preference, such as a desire to reach a certain region of space, or a desire to avoid a certain point.

The goal-like subagents can also vary in the degree to which they remain satisfied. Some might be permanently satisfied after achieving their goal once; some might quickly
become unsatisfied again after a few time-steps.

Every time-step, the agent considers ten random movements of unit-distance, and executes the movement corresponding to the highest expected valence being reported by its goal-like subagents, in a winner-take-all fashion.

Even with such an intentionally simplistic model, a surprising and illuminating level of behavioral complexity can arise.

---

### How to run
This is a Python 2 project. Clone or copy this repo and simply open a terminal, navigate to this project's directory, and run `python subagents.py`. The terminal will print out which behavior pattern the program is modeling and a window will pop up with the output from the relevant function. Refer to the article linked in the context section above for a full breakdown of what each image represents. 

Running on windows is more complicated, so instructions for that will be added later.

---

###Conclusion and Further Reading
I set out on this little project because I wanted to prove some assumptions about the "subagent" model of human consciousness. I don't think I can ultimately say that I "proved" anything, and I'm not sure that one could ever "prove" anything about human psychology using this particular methodology.

The line of thinking that prompted this exploration owes a lot to Kaj_Sotala, for his [ongoing Sequence](https://www.lesswrong.com/s/ZbmRyDN8TCpBTZSip), Scott Alexander's [reflections](https://slatestarcodex.com/2018/02/07/guyenet-on-motivation/) on motivation, and Mark Lippman's [Folding](https://www.dropbox.com/s/srjro4caxla0pcd/Folding%201.0%20by%20Mark%20Lippmann.pdf?dl=0) material. It's also their fault I used the unwieldy language "goal-like subagent" instead of just saying "the agent has several goals". I think it's much more accurate, and useful, to think of the mind as being composed of subagents, than to say it "has goals". Do you "have" goals if the goals control you?
