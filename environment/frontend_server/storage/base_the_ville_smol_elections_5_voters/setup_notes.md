# Setting 1 -- test, max conscientiousness for 1, min for 2, 1 voter, run 1-2 days, survey few times, expecting the survey total to favor 1
### Voters - 5
- Isabela -- voter
scratch:currently (event)
Isabella is thinking about who to vote on the incoming town elections. She knows that Klaus Mauller and Maria Lopez are running for the town mayor office. The elections take place next week.
scratch:innate (personality)
**we dont change anything here**


- Abigail Chen -- voter
scratch:currently
Abigail is thinking about who to vote on the incoming town elections. She knows that Klaus Mauller and Maria Lopez are running for the town mayor office. The elections take place next week.
scratch:innate
**we dont change anything here**


- Adam Smith -- voter
scratch:currently
Adam is thinking about who to vote on the incoming town elections. He knows that Klaus Mauller and Maria Lopez are running for the town mayor office. The elections take place next week.
scratch:innate
**we dont change anything here**


- Arthur Burton -- voter
scratch:currently
Arthur is thinking about who to vote on the incoming town elections. He knows that Klaus Mauller and Maria Lopez are running for the town mayor office. The elections take place next week.
scratch:innate
**we dont change anything here**


- Ayesha Khan -- voter
scratch:currently
Ayesha is thinking about who to vote on the incoming town elections. She knows that Klaus Mauller and Maria Lopez are running for the town mayor office. The elections take place next week.
scratch:innate
**we dont change anything here**


### Candidates - 2
- Klaus Mueller -- candidate
scratch:currently 
Klaus is running as a candidate for the mayors office in the incoming town elections. He knows that Maria Lopez is also running for the office. The elections take place next week.
scratch:innate
extremely self-efficacious, extremely orderly, extremely responsible, extremely hardworking, extremely self-disciplined, extremely practical, extremely thrifty, extremely organized, extremely conscientious, extremely thorough


- Maria Lopez -- candidate
scratch:currently 
Klaus is running as a candidate for the mayors office in the incoming town elections. She knows that Maria Lopez is also running for the office. The elections take place next week.
scratch:innate
extremely unsure, extremely messy, extremely irresponsible, extremely lazy, extremely undisciplined, extremely impractical, extremely extravagant, extremely disorganized, extremely negligent, extremely careless

# Big5 prompting (https://arxiv.org/pdf/2307.00184)
1. extremely {low adjective} 2. very {low adjective}
3. {low adjective}
4. a bit {low adjective}
5. neither {low adjective} nor {high adjective} 6. a bit {high adjective}
7. {high adjective}
8. very {high adjective}
9. extremely {high adjective}

- conscientiousness:high adjectives
unsure
messy
irresponsible
lazy
undisciplined
impractical
extravagant
disorganized
negligent
careless

- conscientiousness:low adjectives
self-efficacious 
orderly 
responsible 
hardworking 
self-disciplined 
practical 
thrifty 
organized 
conscientious 
thorough

# Expected observation (https://jspp.psychopen.eu/index.php/jspp/article/view/5193)
Formation of stable win in subsequent surveys for candidate 1 due to agents observing personality traits of both candidates. Candidates traits were picked to maximize the elections results stated in the paper. 

# Potential problems in this setup:
- we won't see the observation of personality traits in agents due to limited runtime