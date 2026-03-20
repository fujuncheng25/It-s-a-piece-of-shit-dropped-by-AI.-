#!/usr/bin/env python3
import json
import math
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Tuple

PORT = 9130
OLLAMA_URL = "http://127.0.0.1:11434"
PREFERRED_MODELS = ["llama3.2", "llama3.1", "qwen2.5", "mistral"]
MAX_REQUEST_BYTES = 1_000_000

UVA_KNOWLEDGE = [
    {
        "title": 'College Search Guide paragraph 1',
        "source": "College_Search_Guide(1).docx",
        "text": 'College/University Search Guide',
    },
    {
        "title": 'College Search Guide paragraph 2',
        "source": "College_Search_Guide(1).docx",
        "text": 'Hi 10th grade admission officers! Hope this guide will help you know your representing colleges/universities a little bit better and good luck to your college fair prep!',
    },
    {
        "title": 'College Search Guide paragraph 3',
        "source": "College_Search_Guide(1).docx",
        "text": 'University: University of Virginia',
    },
    {
        "title": 'College Search Guide paragraph 4',
        "source": "College_Search_Guide(1).docx",
        "text": 'Class: 10.6',
    },
    {
        "title": 'College Search Guide paragraph 5',
        "source": "College_Search_Guide(1).docx",
        "text": 'Admission Officers:',
    },
    {
        "title": 'College Search Guide paragraph 6',
        "source": "College_Search_Guide(1).docx",
        "text": '[General Introduction]',
    },
    {
        "title": 'College Search Guide paragraph 7',
        "source": "College_Search_Guide(1).docx",
        "text": 'Mission:',
    },
    {
        "title": 'College Search Guide paragraph 8',
        "source": "College_Search_Guide(1).docx",
        "text": 'The University of Virginia is a public institution of higher learning guided by a founding vision of discovery, innovation, and development of the full potential of talented students from all walks of life. It serves the Commonwealth of Virginia, the nation, and the world by developing responsible citizen leaders and professionals; advancing, preserving, and disseminating knowledge; and providing world-class patient care.',
    },
    {
        "title": 'College Search Guide paragraph 9',
        "source": "College_Search_Guide(1).docx",
        "text": 'We are defined by:',
    },
    {
        "title": 'College Search Guide paragraph 10',
        "source": "College_Search_Guide(1).docx",
        "text": 'Our enduring commitment to a vibrant and unique residential learning environment marked by the free and collegial exchange of ideas;',
    },
    {
        "title": 'College Search Guide paragraph 11',
        "source": "College_Search_Guide(1).docx",
        "text": 'Our unwavering support of a collaborative, diverse community bound together by distinctive foundational values of honor, integrity, trust, and respect;',
    },
    {
        "title": 'College Search Guide paragraph 12',
        "source": "College_Search_Guide(1).docx",
        "text": 'Our universal dedication to excellence and affordable access.',
    },
    {
        "title": 'College Search Guide paragraph 13',
        "source": "College_Search_Guide(1).docx",
        "text": 'History:',
    },
    {
        "title": 'College Search Guide paragraph 14',
        "source": "College_Search_Guide(1).docx",
        "text": "The University of Virginia, abbreviated as 'UVa', is located in Charlottesville, Virginia, USA [26]. It is a public comprehensive research university. It was founded in 1819 by Thomas Jefferson, the third president of the United States and the author of the Declaration of Independence [25]. It was the first university in the United States to be independent of the church and is also an institution listed in the UNESCO World Heritage List.",
    },
    {
        "title": 'College Search Guide paragraph 15',
        "source": "College_Search_Guide(1).docx",
        "text": 'Location:',
    },
    {
        "title": 'College Search Guide paragraph 16',
        "source": "College_Search_Guide(1).docx",
        "text": 'The University of Virginia (UVA) is located in Charlottesville, Virginia. This charming city is approximately 120 miles southwest of Washington, DC ,and offers a pleasant mix of urban and rural settings.',
    },
    {
        "title": 'College Search Guide paragraph 17',
        "source": "College_Search_Guide(1).docx",
        "text": 'Student population:',
    },
    {
        "title": 'College Search Guide paragraph 18',
        "source": "College_Search_Guide(1).docx",
        "text": 'Undergraduate Students on Grounds 18K',
    },
    {
        "title": 'College Search Guide paragraph 19',
        "source": "College_Search_Guide(1).docx",
        "text": 'Graduate and Professional Students on Grounds 9k',
    },
    {
        "title": 'College Search Guide paragraph 20',
        "source": "College_Search_Guide(1).docx",
        "text": 'International Students on Grounds 3k',
    },
    {
        "title": 'College Search Guide paragraph 21',
        "source": "College_Search_Guide(1).docx",
        "text": 'Countries Represented by International Students on Grounds 109',
    },
    {
        "title": 'College Search Guide paragraph 22',
        "source": "College_Search_Guide(1).docx",
        "text": 'School size',
    },
    {
        "title": 'College Search Guide paragraph 23',
        "source": "College_Search_Guide(1).docx",
        "text": 'It has a total undergraduate enrollment of 17,901 (fall 2024), its setting is city, and the campus size is 1,682 acres. The student-faculty ratio at University of Virginia is 14:1, and it utilizes a semester-based academic calendar.',
    },
    {
        "title": 'College Search Guide paragraph 24',
        "source": "College_Search_Guide(1).docx",
        "text": 'School tradition:',
    },
    {
        "title": 'College Search Guide paragraph 25',
        "source": "College_Search_Guide(1).docx",
        "text": 'Academical Village',
    },
    {
        "title": 'College Search Guide paragraph 26',
        "source": "College_Search_Guide(1).docx",
        "text": 'As part of his vision for UVA, Thomas Jefferson wanted students and professors to live as neighbors, to bridge the gap between academic life and student life. Professors would live in the pavilions located around the Lawn, and students would live in the rooms surrounding the Lawn. Also home to the Rotunda, the Lawn is the only UNESCO World Heritage Site located at a college in the United States. The University Guide Service offers historical tours to illuminate the University’s long history and tell the stories of those who built the foundations of UVA. To this day, students and professors still live on the Lawn, showing that this tradition has embedded itself into student life at UVA. You can find the Lawn at the center of student life on Grounds and a few of your classmates in the M.S. in Commerce Program living on the Range. Conveniently, Rouss & Robertson Halls, where classes are held, is located at the south end of the Lawn, making it an excellent location for students to take a quick study break outside when the weather is nice.',
    },
    {
        "title": 'College Search Guide paragraph 27',
        "source": "College_Search_Guide(1).docx",
        "text": 'Secret Societies',
    },
    {
        "title": 'College Search Guide paragraph 28',
        "source": "College_Search_Guide(1).docx",
        "text": 'Secret societies have a long history at UVA. These societies engage in traditions and activities unique to each of their organizations and often donate money to support different clubs and institutions at the University. They also often honor students who aren’t in those societies by inviting them to dinners or recognizing them with letters. You can find many of their logos painted around prominent walking spaces on Grounds. The McIntire School of Commerce even has one of its own that offers awards to students at the end of each year!',
    },
    {
        "title": 'College Search Guide paragraph 29',
        "source": "College_Search_Guide(1).docx",
        "text": 'Honor Code',
    },
    {
        "title": 'College Search Guide paragraph 30',
        "source": "College_Search_Guide(1).docx",
        "text": 'A staple at UVA, the Honor Code states that students will never lie, cheat, or steal. This code is in place to this day, and many students leave their belongings around Grounds or are given take-home exams since the community of trust is so strong here. The Honor Code was previously a single-sanction system, which meant expulsion for those found guilty of a violation. Students have recently voted to remove the single sanction, demonstrating the power of student self-governance. You can learn more about the Honor Code here or during a tour.',
    },
    {
        "title": 'College Search Guide paragraph 31',
        "source": "College_Search_Guide(1).docx",
        "text": 'Convocation and Final Exercises',
    },
    {
        "title": 'College Search Guide paragraph 32',
        "source": "College_Search_Guide(1).docx",
        "text": 'Finally, Convocation and Final Exercises are two traditions you’ll experience with your classmates. At the beginning of their time at UVA, all new students are invited to Convocation, during which they sign the Honor Code and are inducted into the University community. Convocation takes place facing the Rotunda. At the end of their time at UVA, students graduate and face Old Cabell Hall, away from the Rotunda, after walking the Lawn. The tradition symbolizes taking the knowledge they’ve learned at UVA (represented by the Rotunda, which used to be a library) and using it to make a difference in the world (symbolized by the Blue Ridge Mountains, which are located behind Old Cabell Hall). This tradition is a great way to finish your time at UVA with friends you’ve made at the School.',
    },
    {
        "title": 'College Search Guide paragraph 33',
        "source": "College_Search_Guide(1).docx",
        "text": 'Graduation crowd at UVA',
    },
    {
        "title": 'College Search Guide paragraph 34',
        "source": "College_Search_Guide(1).docx",
        "text": 'Student Events',
    },
    {
        "title": 'College Search Guide paragraph 35',
        "source": "College_Search_Guide(1).docx",
        "text": 'While UVA has a rich history, in recent years, it has added many traditions that have quickly become popular among the University community.',
    },
    {
        "title": 'College Search Guide paragraph 36',
        "source": "College_Search_Guide(1).docx",
        "text": 'Trick-or-Treating on the Lawn (TOTOTL)',
    },
    {
        "title": 'College Search Guide paragraph 37',
        "source": "College_Search_Guide(1).docx",
        "text": 'On the Thursday of Halloween Weekend, families in Charlottesville bring their kids and dress up in costumes to go trick-or-treating on the Lawn. This is my absolute favorite event of the year, and it is a nice way to bridge the UVA and Charlottesville communities.',
    },
    {
        "title": 'College Search Guide paragraph 38',
        "source": "College_Search_Guide(1).docx",
        "text": 'Lighting of the Lawn (LOTL)',
    },
    {
        "title": 'College Search Guide paragraph 39',
        "source": "College_Search_Guide(1).docx",
        "text": 'Perhaps the most significant event that takes place every year, Lighting of the Lawn (LOTL) started after 9/11 to bring the community together. The event has since transformed into the huge light show that it is today. LOTL features events at the South Lawn and a capella performances until the light show at night’s end. This is another favorite event of mine (even though I’m biased, since I was on the committee to plan this). If a friend of yours in the program lives in a Lawn Range room, this is a night when they very well may throw a get-together with the program before attending the show.',
    },
    {
        "title": 'College Search Guide paragraph 40',
        "source": "College_Search_Guide(1).docx",
        "text": 'Lighting of the Lawn crowd at UVA',
    },
    {
        "title": 'College Search Guide paragraph 41',
        "source": "College_Search_Guide(1).docx",
        "text": 'Rotunda Sing',
    },
    {
        "title": 'College Search Guide paragraph 42',
        "source": "College_Search_Guide(1).docx",
        "text": 'Rotunda Sing is the first event that happens on Grounds, taking place during Welcome Week and featuring performances from every a capella group. UVA is well regarded for its a capella groups, and it’s a great way to spend time with new friends in the M.S. in Commerce Program.',
    },
    {
        "title": 'College Search Guide paragraph 43',
        "source": "College_Search_Guide(1).docx",
        "text": 'SpringFest',
    },
    {
        "title": 'College Search Guide paragraph 44',
        "source": "College_Search_Guide(1).docx",
        "text": 'SpringFest is the major event that takes place in the spring semester. Hosted by UPC, the event offers free food to students and features musical performances in the University amphitheater. It’s an excellent way to celebrate the nice weather after the cold winter months.',
    },
    {
        "title": 'College Search Guide paragraph 45',
        "source": "College_Search_Guide(1).docx",
        "text": '4th Year 5k',
    },
    {
        "title": 'College Search Guide paragraph 46',
        "source": "College_Search_Guide(1).docx",
        "text": 'The Peer Health Educators host the hugely popular 4th Year 5k, which takes place across Grounds on the morning of the last home football game of the year and concludes at the Lawn, where snacks are available for racers. The event’s male and female winners are honored at the football game, later that day. The 4th year 5k is a great way to end a fun football season (the shirts are also famously nice)!',
    },
    {
        "title": 'College Search Guide paragraph 47',
        "source": "College_Search_Guide(1).docx",
        "text": 'Pancakes for Parkinson’s',
    },
    {
        "title": 'College Search Guide paragraph 48',
        "source": "College_Search_Guide(1).docx",
        "text": 'During Pancakes for Parkinson’s, student volunteers cook pancakes to raise funds for the the Michael J. Fox Foundation. This event, which takes place on the Lawn, often features UVA President Ryan cooking pancakes alongside students and is a great way to be charitable and spend time with friends.',
    },
    {
        "title": 'College Search Guide paragraph 49',
        "source": "College_Search_Guide(1).docx",
        "text": 'These are just a few of the long list of traditions you can expect to participate in at UVA. A more exhaustive list is linked here if you care to explore the different traditions UVA offers',
    },
    {
        "title": 'College Search Guide paragraph 50',
        "source": "College_Search_Guide(1).docx",
        "text": 'Rankings:',
    },
    {
        "title": 'College Search Guide paragraph 51',
        "source": "College_Search_Guide(1).docx",
        "text": '[Academics]',
    },
    {
        "title": 'College Search Guide paragraph 52',
        "source": "College_Search_Guide(1).docx",
        "text": 'Departments &schools:',
    },
    {
        "title": 'College Search Guide paragraph 53',
        "source": "College_Search_Guide(1).docx",
        "text": 'The University of Virginia comprises 12 schools in Charlottesville, the College at Wise in Southwest Virginia, and UVA Northern Virginia representing nine UVA schools in Fairfax and two in Arlington, as well as a comprehensive health system and six pan-University research institutes.',
    },
    {
        "title": 'College Search Guide paragraph 54',
        "source": "College_Search_Guide(1).docx",
        "text": 'Programs of study, majors, minors',
    },
    {
        "title": 'College Search Guide paragraph 55',
        "source": "College_Search_Guide(1).docx",
        "text": 'Research opportunities',
    },
    {
        "title": 'College Search Guide paragraph 56',
        "source": "College_Search_Guide(1).docx",
        "text": 'UVA provides a wide variety of research opportunities work in labs including department of nursing, engineering and applied science, cognitive science and etc.',
    },
    {
        "title": 'College Search Guide paragraph 57',
        "source": "College_Search_Guide(1).docx",
        "text": 'Academic aid',
    },
    {
        "title": 'College Search Guide paragraph 58',
        "source": "College_Search_Guide(1).docx",
        "text": 'UVA combines rigorous studies with the support and advising resources needed to help undergraduate students thriveand reach their academic goals. This commitment to achievement, along with plentiful opportunities for service andleadership as part of a vibrant University community, prepares UVA students for fulfilling lives and careers',
    },
    {
        "title": 'College Search Guide paragraph 59',
        "source": "College_Search_Guide(1).docx",
        "text": 'Academic Pathways',
    },
    {
        "title": 'College Search Guide paragraph 60',
        "source": "College_Search_Guide(1).docx",
        "text": "Areas of study that speak to students' passions will shape their future. UVA ensures students' choices aren't limited, offering many majors, minors and dual-degree opportunities.",
    },
    {
        "title": 'College Search Guide paragraph 61',
        "source": "College_Search_Guide(1).docx",
        "text": 'Academic Support',
    },
    {
        "title": 'College Search Guide paragraph 62',
        "source": "College_Search_Guide(1).docx",
        "text": "Student academic success is the University's toppriority, and it shows. Through programs such as peercoaching and tutoring and STEM support initiatives,every student can thrive.",
    },
    {
        "title": 'College Search Guide paragraph 63',
        "source": "College_Search_Guide(1).docx",
        "text": 'Academic Advising',
    },
    {
        "title": 'College Search Guide paragraph 64',
        "source": "College_Search_Guide(1).docx",
        "text": 'UVA is committed to helping students take advantage of everything the University has to offer with access to resources and services.',
    },
    {
        "title": 'College Search Guide paragraph 65',
        "source": "College_Search_Guide(1).docx",
        "text": 'Find Research Opportunities',
    },
    {
        "title": 'College Search Guide paragraph 66',
        "source": "College_Search_Guide(1).docx",
        "text": 'The team at the Office of Citizen Scholar Development can help undergraduates find opportunities to get started in research. They offer workshops, advising, access to funding, and more.',
    },
    {
        "title": 'College Search Guide paragraph 67',
        "source": "College_Search_Guide(1).docx",
        "text": '…',
    },
    {
        "title": 'College Search Guide paragraph 68',
        "source": "College_Search_Guide(1).docx",
        "text": '[Social life]',
    },
    {
        "title": 'College Search Guide paragraph 69',
        "source": "College_Search_Guide(1).docx",
        "text": 'Residential life',
    },
    {
        "title": 'College Search Guide paragraph 70',
        "source": "College_Search_Guide(1).docx",
        "text": 'Supporting Students, Engaging Leaders',
    },
    {
        "title": 'College Search Guide paragraph 71',
        "source": "College_Search_Guide(1).docx",
        "text": 'We pride ourselves on maintaining a residential program firmly rooted in the spirit of student self-governance. To this end, Housing & Residence Life (HRL) recruits and selects upwards of 240 students each year to serve as peer leaders who are in turn a means of support for their fellow students.',
    },
    {
        "title": 'College Search Guide paragraph 72',
        "source": "College_Search_Guide(1).docx",
        "text": 'Resident Staff\xa0members work closely with a group of dedicated HRL professionals to establish residence halls and apartments as welcoming, secure living areas that represent and promote the high standards of achievement and conduct expected of students at the University of Virginia.',
    },
    {
        "title": 'College Search Guide paragraph 73',
        "source": "College_Search_Guide(1).docx",
        "text": 'Furthermore, students are immediately given the opportunity to lead within their residential community as first years through the\xa0Residential Leadership Experience. Students living on-Grounds are elected to represent their class as a member of the First Year Council or their residence hall in their respective Association Council.',
    },
    {
        "title": 'College Search Guide paragraph 74',
        "source": "College_Search_Guide(1).docx",
        "text": 'Programs and events\xa0sponsored by HRL staff and communities are intended to engage and inform, always in pursuit of our overarching goal to create welcoming communities.',
    },
    {
        "title": 'College Search Guide paragraph 75',
        "source": "College_Search_Guide(1).docx",
        "text": 'Residential Events',
    },
    {
        "title": 'College Search Guide paragraph 76',
        "source": "College_Search_Guide(1).docx",
        "text": 'Programs and events allow us to put our mission in motion. Students and staff work collaboratively to create community, offering special and everyday occasions that engage and educate. We provide facts and information to enrich your day-to-day, but also opportunities that may be memories in the making. It’s all part of a day in the life at UVA.',
    },
    {
        "title": 'College Search Guide paragraph 77',
        "source": "College_Search_Guide(1).docx",
        "text": 'Arts & athletics',
    },
    {
        "title": 'College Search Guide paragraph 78',
        "source": "College_Search_Guide(1).docx",
        "text": 'The arts are central to life at the University of Virginia. UVA offers access to world-class art and performances at Old Cabell Hall, The Fralin Museum of Art, the Kluge-Ruhe Aboriginal Art Collection and three state-of-the-art theaters.',
    },
    {
        "title": 'College Search Guide paragraph 79',
        "source": "College_Search_Guide(1).docx",
        "text": 'Through UVA Arts and signature events, such as the\xa0Virginia Film Festival, the University cultivates a vibrant community that promotes creative expression and unites artists and performers across the commonwealth, nation and world.',
    },
    {
        "title": 'College Search Guide paragraph 80',
        "source": "College_Search_Guide(1).docx",
        "text": "The University of Virginia's athletic program, known as the Cavaliers (or affectionately as the Wahoos), represents a proud and integral part of the institution's commitment to educational excellence\xa0. Competing in the Atlantic Coast Conference (ACC) at the NCAA Division I level, UVA fields 27 varsity sports and has established itself as a national powerhouse\xa0. The Cavaliers have captured numerous NCAA championships across a diverse range of sports, including historic dominance in men's soccer (with seven titles), sustained success in men's lacrosse (five NCAA titles), a thrilling baseball College World Series victory in 2015, and a recent unprecedented five-peat by the women's swimming and diving team\xa0. This tradition of excellence extends from iconic venues like Scott Stadium and John Paul Jones Arena to the athletes themselves, who are defined by their pursuit of championships, academic achievement, and service to the community",
    },
    {
        "title": 'College Search Guide paragraph 81',
        "source": "College_Search_Guide(1).docx",
        "text": '[Study abroad opportunities]',
    },
    {
        "title": 'College Search Guide paragraph 82',
        "source": "College_Search_Guide(1).docx",
        "text": 'Curriculum and Learning | UVA SCPS',
    },
    {
        "title": 'College Search Guide paragraph 83',
        "source": "College_Search_Guide(1).docx",
        "text": '…',
    },
    {
        "title": 'College Search Guide paragraph 84',
        "source": "College_Search_Guide(1).docx",
        "text": '[Career development]',
    },
    {
        "title": 'College Search Guide paragraph 85',
        "source": "College_Search_Guide(1).docx",
        "text": 'UVA Career Center',
    },
    {
        "title": 'College Search Guide paragraph 86',
        "source": "College_Search_Guide(1).docx",
        "text": 'The UVA Career Center supports all UVA students and serves as a central hub for satellite career services offices that are embedded in other colleges on Grounds. By engaging with Career Counselors, UVA Alumni networks, and industry-specific opportunities, the UVA Career Center enables students of all years to create the foundation of their career journey while at the University.',
    },
    {
        "title": 'College Search Guide paragraph 87',
        "source": "College_Search_Guide(1).docx",
        "text": 'Global Internships Office (GIO)',
    },
    {
        "title": 'College Search Guide paragraph 88',
        "source": "College_Search_Guide(1).docx",
        "text": 'Exploring applied learning opportunities abroad. There are many avenues to explore if you are keen to apply the skills and knowledge you have developed in the classroom to real-world international settings.',
    },
    {
        "title": 'College Search Guide paragraph 89',
        "source": "College_Search_Guide(1).docx",
        "text": 'Reports & statistics',
    },
    {
        "title": 'College Search Guide paragraph 90',
        "source": "College_Search_Guide(1).docx",
        "text": '…',
    },
    {
        "title": 'College Search Guide paragraph 91',
        "source": "College_Search_Guide(1).docx",
        "text": '[Admission requirement]',
    },
    {
        "title": 'College Search Guide paragraph 92',
        "source": "College_Search_Guide(1).docx",
        "text": 'Characteristics & Qualities of Competitive Applicants',
    },
    {
        "title": 'College Search Guide paragraph 93',
        "source": "College_Search_Guide(1).docx",
        "text": 'Students who are academically successful, capable and/or have the potential to contribute to our vibrant intellectual community at UVA',
    },
    {
        "title": 'College Search Guide paragraph 94',
        "source": "College_Search_Guide(1).docx",
        "text": "Successful applicants are students who have done well academically within the context of their high school or college setting, based on their coursework and grades. While taking into consideration what is offered and recommended within a student's school, we are interested in applicants who embrace academic challenges across the curriculum, and who are successful within the classroom space.",
    },
    {
        "title": 'College Search Guide paragraph 95',
        "source": "College_Search_Guide(1).docx",
        "text": "We are looking for students who love to learn, solve problems, and are actively engaged with peers in the classroom. These students might have a breadth of academic interests, or they might be more singularly focused on one area of study in college. Most first year applicants are unsure of their intended major or college course of study when they apply, and that is fine. A student's academic focus is only a factor when it applies to their choice of undergraduate school at UVA. First year applicants applying to the College of Arts and Sciences, and Schools of Architecture, Education (Kinesiology), Engineering, and Nursing are reviewed by separate admission teams. The same is true for transfer students who are also able to apply to the Batten School of Public Policy and Leadership and the School of Commerce as well as our Teaching, Youth and Social Innovation, and Speech Communication Disorders programs in the School of Education.",
    },
    {
        "title": 'College Search Guide paragraph 96',
        "source": "College_Search_Guide(1).docx",
        "text": "We welcome first year applications from, and offer admission to, students who have grown and evolved as students and young adults while in high school. Applicants do not have to present a perfect academic transcript with all A's and double-digit AP courses to be competitive to UVA as a first-year student, but we do look for applicants who have the ability to contribute to the academic life of the University.",
    },
    {
        "title": 'College Search Guide paragraph 97',
        "source": "College_Search_Guide(1).docx",
        "text": "We do not use an algorithm or formula when making admission decisions and we do not have thresholds for GPA's, test scores, or the number of AP, IB, dual enrollment, or Cambridge courses a student must take to be eligible for admission. Each applicant is unique and is reviewed within the context of their unique backgrounds, experiences, opportunities, and challenges. Applicants are encouraged to share these stories and this context, and how they have been shaped by them, in their applications.",
    },
    {
        "title": 'College Search Guide paragraph 98',
        "source": "College_Search_Guide(1).docx",
        "text": 'Students with potential to live lives of purpose, impact, and service to others',
    },
    {
        "title": 'College Search Guide paragraph 99',
        "source": "College_Search_Guide(1).docx",
        "text": 'Understanding that students have different opportunities based on their background, school, and community, we look for students who have the potential to make a difference in their community, in the UVA community, and in the world. UVA will support students to help them reach that potential.',
    },
    {
        "title": 'College Search Guide paragraph 100',
        "source": "College_Search_Guide(1).docx",
        "text": "We seek students who engage in impactful activities and experiences within their schools and communities, and we are especially interested in how these activities and experiences have shaped their character, skills, and knowledge. These activities need not be high school sponsored organizations or events, nor do they need to consume a student's life. We do not count the number of clubs or teams a student has been involved with during high school in order to predict their level of involvement in these, or other, organizations at UVA. We simply invite students, and those who recommend them, to share information with us that will help us to get to know the applicant as an active member of their family, high school, town, or community.",
    },
    {
        "title": 'College Search Guide paragraph 101',
        "source": "College_Search_Guide(1).docx",
        "text": 'We are deeply interested in students who show kindness, care, and compassion to others and demonstrate character and integrity in all they do.',
    },
    {
        "title": 'College Search Guide paragraph 102',
        "source": "College_Search_Guide(1).docx",
        "text": 'We are interested in students who directly or indirectly lead others, or who have the potential to lead, ethically and collaboratively. Students might demonstrate leadership in a variety of ways: leading school or community-based organizations, leading in their home or work, leading in the classroom, or leading by example through their character, work ethic, and an ability to build bridges.',
    },
    {
        "title": 'College Search Guide paragraph 103',
        "source": "College_Search_Guide(1).docx",
        "text": 'Students who demonstrate a determination to succeed',
    },
    {
        "title": 'College Search Guide paragraph 104',
        "source": "College_Search_Guide(1).docx",
        "text": 'Some students may have overcome significant challenges or shown unusual resilience in their pursuit of success. They may have succeeded in spite of limited opportunities, advantages or expectations. They may show an unusual determination in their studies, extending beyond the classroom space with their pursuit of knowledge. We encourage students to share with us any information that they feel would help us better get to know them, academically or personally.',
    },
    {
        "title": 'College Search Guide paragraph 105',
        "source": "College_Search_Guide(1).docx",
        "text": 'Consistent with federal and state law, the University of Virginia does not consider a student’s racial or ethnic status, or the student’s status as the relative of a UVA graduate or a donor to UVA, when making admission decisions.  Although students are free to discuss any aspects of their individual experiences in their applications, any such discussion of racial, ethnic, or relationship status will only be considered if it is tied to the student’s unique ability to contribute to the University.',
    },
    {
        "title": 'College Search Guide paragraph 106',
        "source": "College_Search_Guide(1).docx",
        "text": 'Application cycles & deadlines',
    },
    {
        "title": 'College Search Guide paragraph 107',
        "source": "College_Search_Guide(1).docx",
        "text": 'Application Review Process',
    },
    {
        "title": 'College Search Guide paragraph 108',
        "source": "College_Search_Guide(1).docx",
        "text": 'Our holistic approach to the application process allows us to consider many factors as we read applications and make admission decisions. We do not use a formula, equation, or algorithm during our review.',
    },
    {
        "title": 'College Search Guide paragraph 109',
        "source": "College_Search_Guide(1).docx",
        "text": 'We take great care to ensure that the application review is comprehensive, thoughtful, and personal. We are grateful to every applicant who has put their faith in us. As such, every application is read by at least one member of our evaluation team and all applications are handled with the utmost respect.',
    },
    {
        "title": 'College Search Guide paragraph 110',
        "source": "College_Search_Guide(1).docx",
        "text": 'We employ approximately 60 application readers each year. Application readers are often assigned to an evaluation team that is responsible for a geographic region of the state, country, or world. For our first-year application review we divide the regions into several groups:',
    },
    {
        "title": 'College Search Guide paragraph 111',
        "source": "College_Search_Guide(1).docx",
        "text": 'Virginians (subdivided by high school or region of the state)',
    },
    {
        "title": 'College Search Guide paragraph 112',
        "source": "College_Search_Guide(1).docx",
        "text": 'Non-Virginians who attend high school in the US, and',
    },
    {
        "title": 'College Search Guide paragraph 113',
        "source": "College_Search_Guide(1).docx",
        "text": 'International applicants and US citizens/Permanent Residents who live abroad.',
    },
    {
        "title": 'College Search Guide paragraph 114',
        "source": "College_Search_Guide(1).docx",
        "text": 'Students from these groups are in separate and distinct application pools therefore they are not competing directly with one another for a space in the class. Similarly, students applying to different UVA schools (Arts & Sciences, Engineering, Architecture, Nursing, Education, etc.) are not in the same application pool and are not competing with one another.',
    },
    {
        "title": 'College Search Guide paragraph 115',
        "source": "College_Search_Guide(1).docx",
        "text": 'Each year we seek to enroll a balance of Virginians and non-Virginians. Most years that balance is approximately 70% Virginian overall. International students are included in the non-Virginian applicant pool and make up approximately 5-6% of the incoming first year students. There are ~3,970 new first year students each fall and ~600 fall transfers. The University also enrolls a small (60-70 students) cohort of transfers in the spring term.',
    },
    {
        "title": 'College Search Guide paragraph 116',
        "source": "College_Search_Guide(1).docx",
        "text": 'First year students can apply using our Early Decision, Early Action, or Regular Decision plan. Admission rates vary each year but there is no advantage applying to one plan over the other. We offer the exact same financial aid award, regardless of the admission plan. For context, approximately 10% of the total number of offers of admission are made in our Early Decision round.',
    },
    {
        "title": 'College Search Guide paragraph 117',
        "source": "College_Search_Guide(1).docx",
        "text": 'We seek to enroll students and classes that are in-line with our institutional mission and values. Our students bring with them different opinions, beliefs, backgrounds, life experiences, and political leanings. They come from every corner of the state and globe, and many are the first in their families to attend college.',
    },
    {
        "title": 'College Search Guide paragraph 118',
        "source": "College_Search_Guide(1).docx",
        "text": "Race is not a factor in admission decisions. Neither is a student's family history with UVA. We do not have check boxes for race or UVA family affiliation on our application or on our application review form used by readers. At no point during our review does anyone involved in reading applications have access to reports or collective class data that includes race, ethnicity, or family tie to UVA. However, a student's life experience - which can include race/ethnicity, first generation student status, gender, neighborhood, etc. - can be included and we invite students to share any information they feel would help us get to know them on their Common Application.",
    },
    {
        "title": 'College Search Guide paragraph 119',
        "source": "College_Search_Guide(1).docx",
        "text": 'Admission rates vary depending upon the school and year and are largely driven by application volume. The majority of applicants are capable of being successful students at UVA and we cannot offer admission to every qualified applicant. We are eager to help students find a pathway to UVA through our first-year review or transfer process and we are happy to assist students and families as they make their college decisions.',
    },
    {
        "title": 'College Search Guide paragraph 120',
        "source": "College_Search_Guide(1).docx",
        "text": 'Large Language Models/ Generative AI',
    },
    {
        "title": 'College Search Guide paragraph 121',
        "source": "College_Search_Guide(1).docx",
        "text": 'We are interested in who you are, and we value what you have to say. While AI tools can be helpful in generating ideas and centering your thoughts, essays and personal statements that rely more on AI than your original thoughts miss the mark in one incredibly important way: they lack your voice, your ideas, and your very personal reflection on how your experiences have shaped you.',
    },
    {
        "title": 'College Search Guide paragraph 122',
        "source": "College_Search_Guide(1).docx",
        "text": 'The essays and written supplements are your opportunity to express what is important to you in your own words. Generative AI may play a minor role in your final product by helping you brainstorm essay topics or check for grammar mistakes, but we ask that you do not cut and paste any part of your essay or personal statements from an AI tool. All final submitted materials should be your original work.',
    },
    {
        "title": 'College Search Guide paragraph 123',
        "source": "College_Search_Guide(1).docx",
        "text": 'As an applicant to UVA, we ask you to sign an honor statement before submitting the Common Application because the UVA community is anchored by trust and integrity. Our students pledge not to lie, cheat, or steal, and we ask the same of our applicants. By agreeing to this honor statement, you are pledging that the application materials you submit to us are your original work, not primarily a product of AI. Thank you for trusting us with your words and your stories.',
    },
    {
        "title": 'College Search Guide paragraph 124',
        "source": "College_Search_Guide(1).docx",
        "text": 'Early Decision vs. Early Action vs. Regular Decision',
    },
    {
        "title": 'College Search Guide paragraph 125',
        "source": "College_Search_Guide(1).docx",
        "text": 'We maintain a consistent review throughout the application process so there is no advantage to choosing one application plan over another. We hope to offer students multiple options and the ability to choose the option that is best suited for them. All students applying for financial aid who have submitted the required documents by the priority deadlines will receive a preliminary aid award shortly after admission decisions are released. Below is additional information about our application choices.',
    },
    {
        "title": 'College Search Guide paragraph 126',
        "source": "College_Search_Guide(1).docx",
        "text": 'Early Decision\xa0is a binding admission plan for students who have determined that UVA is their first\xa0choice and who feel they can present a strong application without senior grades being reviewed. Students admitted through the Early Decision admission plan are required to cancel their applications elsewhere and enroll in UVA. Decisions of admit, deny, or defer will be released by December 15th. Admitted students are expected to submit deposits by January 15.',
    },
    {
        "title": 'College Search Guide paragraph 127',
        "source": "College_Search_Guide(1).docx",
        "text": 'Early Action\xa0is a non-binding and unrestrictive admission plan that may be an attractive option for those\xa0feel they\xa0can present a strong application without senior grades being reviewed. We aim to release\xa0decisions of admit, deny, or defer by February 15th. Students admitted through the Early Action admission plan will have until May 1 to reserve a spot by in the incoming class.',
    },
    {
        "title": 'College Search Guide paragraph 128',
        "source": "College_Search_Guide(1).docx",
        "text": 'Regular Decision\xa0is a non-binding and unrestrictive admission plan that allows students more time to complete the application and to have grades from the first term of their senior year considered in the review. Students will be notified of their admission decisions of admit, deny, or waiting list by April 1 Students admitted through the Regular Decision admission plan will have until May 1 to reserve a spot in the incoming class.',
    },
    {
        "title": 'College Search Guide paragraph 129',
        "source": "College_Search_Guide(1).docx",
        "text": 'If you would like to change your chosen plan\xa0for Early Decision or Early Action, you must\xa0email us\xa0by 5 PM on November 6th.',
    },
    {
        "title": 'College Search Guide paragraph 130',
        "source": "College_Search_Guide(1).docx",
        "text": 'School Choice & Academic Interests',
    },
    {
        "title": 'College Search Guide paragraph 131',
        "source": "College_Search_Guide(1).docx",
        "text": 'There are eight undergraduate schools at UVA. First-year applicants can apply to:',
    },
    {
        "title": 'College Search Guide paragraph 132',
        "source": "College_Search_Guide(1).docx",
        "text": 'College of Arts & Sciences',
    },
    {
        "title": 'College Search Guide paragraph 133',
        "source": "College_Search_Guide(1).docx",
        "text": 'School of Architecture',
    },
    {
        "title": 'College Search Guide paragraph 134',
        "source": "College_Search_Guide(1).docx",
        "text": 'School of Engineering',
    },
    {
        "title": 'College Search Guide paragraph 135',
        "source": "College_Search_Guide(1).docx",
        "text": 'School of Nursing',
    },
    {
        "title": 'College Search Guide paragraph 136',
        "source": "College_Search_Guide(1).docx",
        "text": 'Kinesiology',
    },
    {
        "title": 'College Search Guide paragraph 137',
        "source": "College_Search_Guide(1).docx",
        "text": 'Those interested in the McIntire School of Commerce, Batten School for Leadership and Public Policy, School of Data Science, or programs in the School of Education and Human Development other than Kinesiology should apply to the College of Arts and Sciences.',
    },
    {
        "title": 'College Search Guide paragraph 138',
        "source": "College_Search_Guide(1).docx",
        "text": 'You may list two academic interests in addition to your undergraduate school choice. Unless you are applying to the School of Nursing or Kinesiology program, you will not declare a major at UVA until the end of your first or second year.',
    },
    {
        "title": 'College Search Guide paragraph 139',
        "source": "College_Search_Guide(1).docx",
        "text": 'You may change your school/program of entry by emailing us by 5 PM on November 22nd (Early Decision/Early Action) and January 15th (Regular Decision). Admitted students should plan to enroll in the school to which they have applied.',
    },
    {
        "title": 'College Search Guide paragraph 140',
        "source": "College_Search_Guide(1).docx",
        "text": 'Transfer students, please consider the transfer course requirements for each school when making your selection.',
    },
    {
        "title": 'College Search Guide paragraph 141',
        "source": "College_Search_Guide(1).docx",
        "text": 'Standardized Testing',
    },
    {
        "title": 'College Search Guide paragraph 142',
        "source": "College_Search_Guide(1).docx",
        "text": 'Test Optional',
    },
    {
        "title": 'College Search Guide paragraph 143',
        "source": "College_Search_Guide(1).docx",
        "text": "If you're applying for first year admission for Fall 2026, you'll have the choice of sharing or not sharing standardized test scores. Whichever path you choose, we'll consider your application with care and respect, and you won't be disadvantaged because of the choice you've made. The transfer process remains test optional.",
    },
    {
        "title": 'College Search Guide paragraph 144',
        "source": "College_Search_Guide(1).docx",
        "text": 'You may change your test optional decision by\xa0emailing us\xa0by 5 PM on November 22nd (Early Decision/Early Action) and January 15th (Regular Decision).',
    },
    {
        "title": 'College Search Guide paragraph 145',
        "source": "College_Search_Guide(1).docx",
        "text": 'Reporting Scores',
    },
    {
        "title": 'College Search Guide paragraph 146',
        "source": "College_Search_Guide(1).docx",
        "text": 'Applicants who wish to have SAT, ACT, AP, or IB testing considered during the application process should opt to submit scores and self-report them on the application. After the deadline, applicants may submit updated scores through their portal. Admitted students who applied with testing and decide to enroll at UVA must request official score reports for verification. Our ETS code is 5820. Our ACT code is 4412.',
    },
    {
        "title": 'College Search Guide paragraph 147',
        "source": "College_Search_Guide(1).docx",
        "text": 'Super-scoring',
    },
    {
        "title": 'College Search Guide paragraph 148',
        "source": "College_Search_Guide(1).docx",
        "text": 'Super-scoring has been the a long-held practice at UVA. For applicants submitting\xa0test scores, we consider the best combination of section scores without recalculation. Report your scores (section scores for the SAT or composite and sub-scores for the ACT) as they appear on your official score report. Our system will do the rest for you.',
    },
    {
        "title": 'College Search Guide paragraph 149',
        "source": "College_Search_Guide(1).docx",
        "text": 'The\xa0ACT Writing sections are not used in our review.',
    },
    {
        "title": 'College Search Guide paragraph 150',
        "source": "College_Search_Guide(1).docx",
        "text": 'TOEFL/IELTS',
    },
    {
        "title": 'College Search Guide paragraph 151',
        "source": "College_Search_Guide(1).docx",
        "text": 'Students whose first language is not English or who have attended an English-speaking school for fewer than two years are encouraged to provide evidence of their English proficiency by submitting the results of the TOEFL or the IELTS.',
    },
    {
        "title": 'College Search Guide paragraph 152',
        "source": "College_Search_Guide(1).docx",
        "text": 'School Forms & Recommendations',
    },
    {
        "title": 'College Search Guide paragraph 153',
        "source": "College_Search_Guide(1).docx",
        "text": 'We require the secondary school report and one teacher evaluation from an academic subject teacher for each first-year application.',
    },
    {
        "title": 'College Search Guide paragraph 154',
        "source": "College_Search_Guide(1).docx",
        "text": 'Your school counselor can submit the secondary school report online. A counselor recommendation can be submitted with the secondary school report. Your academic teacher recommendation should also be submitted online. In addition to the secondary school report, your counselor should submit the school profile and your transcript(s) online.',
    },
    {
        "title": 'College Search Guide paragraph 155',
        "source": "College_Search_Guide(1).docx",
        "text": 'If your counselor is unable to write a recommendation letter, please request that the secondary school report still be completed and submitted online. If your counselor is unable to provide a written recommendation, you may submit a recommendation from another school administrator or academic teacher if possible. Please know that in this situation, a counselor recommendation is not required for your application to be reviewed.',
    },
    {
        "title": 'College Search Guide paragraph 156',
        "source": "College_Search_Guide(1).docx",
        "text": 'If your school is unable to submit these documents electronically, they can be mailed.',
    },
    {
        "title": 'College Search Guide paragraph 157',
        "source": "College_Search_Guide(1).docx",
        "text": 'Arts & Architecture Supplements',
    },
    {
        "title": 'College Search Guide paragraph 158',
        "source": "College_Search_Guide(1).docx",
        "text": 'Arts Supplements',
    },
    {
        "title": 'College Search Guide paragraph 159',
        "source": "College_Search_Guide(1).docx",
        "text": 'The Admission Office actively seeks artists, musicians, dancers and students in all areas of theatre to invigorate our community through their dedication to the arts.Students who exhibit exceptional talent in the arts may\xa0submit an arts portfolio\xa0through the Common Application via Slideroom. This portfolio is an\xa0optional\xa0part of the application process and is intended for those who plan to engage seriously in the University’s arts departments as students.\xa0Completed portfolio evaluations are shared with the admission committee and are considered as part of the overall application review.\xa0These portfolios are not required to enroll in arts-related classes at the University of Virginia and will only be used for the admission process. If a student who has already submitted their Common App wants to submit an art supplement, they may\xa0create a Slideroom account\xa0using their Common App ID.',
    },
    {
        "title": 'College Search Guide paragraph 160',
        "source": "College_Search_Guide(1).docx",
        "text": 'Supplemental portfolios must be received by the application deadline and\xa0adhere to departmental guidelines\xa0to guarantee review.',
    },
    {
        "title": 'College Search Guide paragraph 161',
        "source": "College_Search_Guide(1).docx",
        "text": 'Architecture Supplements',
    },
    {
        "title": 'College Search Guide paragraph 162',
        "source": "College_Search_Guide(1).docx",
        "text": 'All transfer applicants interested in majoring in Architecture are required to\xa0submit a portfolio following the guidelines and submission requirements\xa0on the School of Architecture website. Transfer applicants interested in Urban Planning and Architectural History are not required to submit portfolios.',
    },
    {
        "title": 'College Search Guide paragraph 163',
        "source": "College_Search_Guide(1).docx",
        "text": 'Residency',
    },
    {
        "title": 'College Search Guide paragraph 164',
        "source": "College_Search_Guide(1).docx",
        "text": 'If you wish to claim entitlement to Virginia in-state educational privileges pursuant to the Code of Virginia, Section 23-7.4, you must complete the residency section of the application. If supporting documents are requested after an application is submitted, fax them to\xa0434-982-2663. See\xa0the Office of Virginia Status website for more information.',
    },
    {
        "title": 'College Search Guide paragraph 165',
        "source": "College_Search_Guide(1).docx",
        "text": 'Demonstrated Interest',
    },
    {
        "title": 'College Search Guide paragraph 166',
        "source": "College_Search_Guide(1).docx",
        "text": 'We do not track attendance at tours, information sessions, high school visits, or other programs (commonly referred to as demonstrated interest)\xa0to use during the application review.',
    },
    {
        "title": 'College Search Guide paragraph 167',
        "source": "College_Search_Guide(1).docx",
        "text": 'Submitting Updates After Deadline',
    },
    {
        "title": 'College Search Guide paragraph 168',
        "source": "College_Search_Guide(1).docx",
        "text": 'All application updates should be uploaded via the student portal. Applicants received an email with login credentials for the portal a few days after their Common App was received. Once the "upload" button is clicked for a document, it is automatically added to your file and will be visible to admission staff. Only required components are shown on the checklist in the portal.',
    },
    {
        "title": 'College Search Guide paragraph 169',
        "source": "College_Search_Guide(1).docx",
        "text": 'Please do not email updates or duplicates to admission officers.',
    },
    {
        "title": 'College Search Guide paragraph 170',
        "source": "College_Search_Guide(1).docx",
        "text": 'Large Language Models/Generative AI',
    },
    {
        "title": 'College Search Guide paragraph 171',
        "source": "College_Search_Guide(1).docx",
        "text": 'We are interested in who you are, and we value what you have to say. While AI tools can be helpful in generating ideas and centering your thoughts, essays and personal statements that rely more on AI than your original thoughts miss the mark in one incredibly important way: they lack your voice, your ideas, and your very personal reflection on how your experiences have shaped you.',
    },
    {
        "title": 'College Search Guide paragraph 172',
        "source": "College_Search_Guide(1).docx",
        "text": 'The essays and written supplements are your opportunity to express what is important to you in your own words. Generative AI may play a minor role in your final product by helping you brainstorm essay topics or check for grammar mistakes, but we ask that you do not cut and paste any part of your essay or personal statements from an AI tool. All final submitted materials should be your original work.',
    },
    {
        "title": 'College Search Guide paragraph 173',
        "source": "College_Search_Guide(1).docx",
        "text": 'As an applicant to UVA, we ask you to sign an honor statement before submitting the Common Application because the UVA community is anchored by trust and integrity. Our students pledge not to lie, cheat, or steal, and we ask the same of our applicants. By agreeing to this honor statement, you are pledging that the application materials you submit to us are your original work, not primarily a product of AI. Thank you for trusting us with your words and your stories.',
    },
    {
        "title": 'College Search Guide paragraph 174',
        "source": "College_Search_Guide(1).docx",
        "text": 'Statistics',
    },
    {
        "title": 'College Search Guide paragraph 175',
        "source": "College_Search_Guide(1).docx",
        "text": 'The statistics below are the result of a holistic application review process. We do not have GPA or testing cut-offs or targets. While we do seek to maintain a 2/3 majority of Virginians in our student population, we do not have quotas for specific high schools, towns, counties, or regions.',
    },
    {
        "title": 'College Search Guide paragraph 176',
        "source": "College_Search_Guide(1).docx",
        "text": 'FAQ (Frequently asked questions)',
    },
    {
        "title": 'College Search Guide paragraph 177',
        "source": "College_Search_Guide(1).docx",
        "text": 'When will I get an admission decision?',
    },
    {
        "title": 'College Search Guide paragraph 178',
        "source": "College_Search_Guide(1).docx",
        "text": 'Early Decision applicants can expect decisions on or around December 15th. Early Action applicants can expect decisions by February 15. Regular Decision applicants can expect decisions by April 1. Keep an eye on the admission blog and our social media accounts for updates!',
    },
    {
        "title": 'College Search Guide paragraph 179',
        "source": "College_Search_Guide(1).docx",
        "text": 'Does UVA offer application fee waivers?',
    },
    {
        "title": 'College Search Guide paragraph 180',
        "source": "College_Search_Guide(1).docx",
        "text": 'Yes. You are eligible to receive an application fee waiver if:',
    },
    {
        "title": 'College Search Guide paragraph 181',
        "source": "College_Search_Guide(1).docx",
        "text": 'You are enrolled in or eligible to participate in the federal free or reduced price lunch program.',
    },
    {
        "title": 'College Search Guide paragraph 182',
        "source": "College_Search_Guide(1).docx",
        "text": 'You have received or are eligible to receive and SAT or ACT fee waiver.',
    },
    {
        "title": 'College Search Guide paragraph 183',
        "source": "College_Search_Guide(1).docx",
        "text": 'Your annual family income falls within the income eligibility guidelines set by the USDA Food and Nutrition Service.',
    },
    {
        "title": 'College Search Guide paragraph 184',
        "source": "College_Search_Guide(1).docx",
        "text": 'Your family receives public assistance.',
    },
    {
        "title": 'College Search Guide paragraph 185',
        "source": "College_Search_Guide(1).docx",
        "text": 'You are enrolled in a federal, state, or local program that aids students from low-income families (e.g., GEAR UP, TRIO such as Upward Bound or others).',
    },
    {
        "title": 'College Search Guide paragraph 186',
        "source": "College_Search_Guide(1).docx",
        "text": 'You live in a federally subsidized public housing, a foster home or are homeless.',
    },
    {
        "title": 'College Search Guide paragraph 187',
        "source": "College_Search_Guide(1).docx",
        "text": 'You are a ward of the state or an orphan.',
    },
    {
        "title": 'College Search Guide paragraph 188',
        "source": "College_Search_Guide(1).docx",
        "text": 'You have received or are eligible to receive a Pell Grant.',
    },
    {
        "title": 'College Search Guide paragraph 189',
        "source": "College_Search_Guide(1).docx",
        "text": 'You can provide a supporting statement from a school official, college access counselor, financial aid officer, or community leader.',
    },
    {
        "title": 'College Search Guide paragraph 190',
        "source": "College_Search_Guide(1).docx",
        "text": 'Students who do not meet any of these criteria but would like to request a fee waiver based on extenuating circumstances should contact the Office of Admission.',
    },
    {
        "title": 'College Search Guide paragraph 191',
        "source": "College_Search_Guide(1).docx",
        "text": 'Does UVA super-score the SAT or ACT?',
    },
    {
        "title": 'College Search Guide paragraph 192',
        "source": "College_Search_Guide(1).docx",
        "text": 'For applicants submitting\xa0test scores, it has been the Office of Admission’s long-standing policy to consider the best test scores submitted by applicants. We use the top score from each SAT section across all administrations of the same exam.\xa0We hope you will submit all of your scores knowing that we will recombine the sections to get the best possible set of scores. If reporting an\xa0ACT score, report the composite and sub-scores as they appear on your official score report\xa0without any recalculation.',
    },
    {
        "title": 'College Search Guide paragraph 193',
        "source": "College_Search_Guide(1).docx",
        "text": 'Can I submit a recommendation from someone who knows me outside of school?',
    },
    {
        "title": 'College Search Guide paragraph 194',
        "source": "College_Search_Guide(1).docx",
        "text": 'We require one recommendation from a teacher of an academic subject so that we can learn more about your school performance. While you are welcome to submit an extra recommendation, we prefer letters that provide insight into your classroom style.',
    },
    {
        "title": 'College Search Guide paragraph 195',
        "source": "College_Search_Guide(1).docx",
        "text": 'Members of the UVA community may submit recommendations using\xa0this form.',
    },
    {
        "title": 'College Search Guide paragraph 196',
        "source": "College_Search_Guide(1).docx",
        "text": 'Will you fill the majority of the class through Early Decision?',
    },
    {
        "title": 'College Search Guide paragraph 197',
        "source": "College_Search_Guide(1).docx",
        "text": 'We will\xa0not fill our class during the Early Decision\xa0process. We hope that you will submit your application when you feel it is in a strong position. Remember that Regular Decision applicants will have grades from the first semester of senior year in their files before we finalize our decisions.',
    },
    {
        "title": 'College Search Guide paragraph 198',
        "source": "College_Search_Guide(1).docx",
        "text": 'What percentage of applicants are admitted?',
    },
    {
        "title": 'College Search Guide paragraph 199',
        "source": "College_Search_Guide(1).docx",
        "text": 'We have pledged to maintain a 2/3 majority of Virginia residents in our student population, but 2/3 of our applicants tend to come from out-of-state. As a result, our offer rate for Virginia residents tends to be much higher than the rate for out-of-state students. Last year, we admitted 25.5% of the Virginia residents and 13% of the non-Virginians. You can see data\xa0from previous years\xa0on the Office of Institutional Assessment website.',
    },
    {
        "title": 'College Search Guide paragraph 200',
        "source": "College_Search_Guide(1).docx",
        "text": "Is a student's level of interest used in the selection process?",
    },
    {
        "title": 'College Search Guide paragraph 201',
        "source": "College_Search_Guide(1).docx",
        "text": 'No. When we read your application, we will not use previous contact as a factor in our review.',
    },
    {
        "title": 'College Search Guide paragraph 202',
        "source": "College_Search_Guide(1).docx",
        "text": 'What AP/IB/A level scores do I need to get credit?',
    },
    {
        "title": 'College Search Guide paragraph 203',
        "source": "College_Search_Guide(1).docx",
        "text": 'We generally give credit for scores of 4 or 5 on AP exams and 5, 6, or 7 on Higher Level IB exams. There are some exceptions to this and practices can vary from one school to another.\xa0The Undergraduate Record\xa0has specific information about AP and IB credit.',
    },
    {
        "title": 'College Search Guide paragraph 204',
        "source": "College_Search_Guide(1).docx",
        "text": 'Does UVA prefer AP, IB, Cambridge or dual enrolled curricula?',
    },
    {
        "title": 'College Search Guide paragraph 205',
        "source": "College_Search_Guide(1).docx",
        "text": 'We do not have a preference for one type of course. We suggest that students take advantage of advanced course options at their high school, regardless of the type of curriculum available.',
    },
    {
        "title": 'College Search Guide paragraph 206',
        "source": "College_Search_Guide(1).docx",
        "text": 'Do you prefer applicants submit the SAT or ACT?',
    },
    {
        "title": 'College Search Guide paragraph 207',
        "source": "College_Search_Guide(1).docx",
        "text": 'We are test optional for the Fall 2026 cycle and have no preference between the SAT and ACT.',
    },
    {
        "title": 'College Search Guide paragraph 208',
        "source": "College_Search_Guide(1).docx",
        "text": 'What minimum GPA and test scores do I need to be admitted?',
    },
    {
        "title": 'College Search Guide paragraph 209',
        "source": "College_Search_Guide(1).docx",
        "text": "We don't have a minimum GPA. We don't have a minimum SAT score.",
    },
    {
        "title": 'College Search Guide paragraph 210',
        "source": "College_Search_Guide(1).docx",
        "text": "As strange as these answers sound, they're both true. A cumulative GPA only reveals so much; it says little about the difficulty of a student's course load, or whether a student's grades have improved over time, or the level of grade inflation (or deflation) in a student's school. If we established a firm minimum GPA, a point below which no applicant would have any chance of being admitted, we'd miss a fair number of students who might make UVA a better, stronger place.",
    },
    {
        "title": 'College Search Guide paragraph 211',
        "source": "College_Search_Guide(1).docx",
        "text": "The same is true for SAT scores. Most people who work in admission at highly selective universities believe that standardized testing is a useful but imprecise instrument. Setting an absolute minimum would be asking these tests to do something they weren't designed to do.",
    },
    {
        "title": 'College Search Guide paragraph 212',
        "source": "College_Search_Guide(1).docx",
        "text": "Of course, our applicant pool is broad and deep, so most admitted students have excelled in school and scored well on the SAT or ACT. But remember that we don't have set minimums for either and we try hard to take into account all of the information we see in each application.",
    },
    {
        "title": 'College Search Guide paragraph 213',
        "source": "College_Search_Guide(1).docx",
        "text": 'International Student & Scholar FAQ: Status, Entry, Rights | International Students & Scholars Program',
    },
    {
        "title": 'College Search Guide paragraph 214',
        "source": "College_Search_Guide(1).docx",
        "text": 'Contact information',
    },
    {
        "title": 'College Search Guide paragraph 215',
        "source": "College_Search_Guide(1).docx",
        "text": 'Admission (Undergraduate)',
    },
    {
        "title": 'College Search Guide paragraph 216',
        "source": "College_Search_Guide(1).docx",
        "text": 'Peabody HallP.O. Box 400160Charlottesville, VA 22903-4160Phone: 434-982-3200',
    },
    {
        "title": 'College Search Guide paragraph 217',
        "source": "College_Search_Guide(1).docx",
        "text": 'Office of Major Events',
    },
    {
        "title": 'College Search Guide paragraph 218',
        "source": "College_Search_Guide(1).docx",
        "text": 'Madison Hall1827 University AvenueCharlottesville, VA 22903Phone: 434-982-3099',
    },
    {
        "title": 'College Search Guide paragraph 219',
        "source": "College_Search_Guide(1).docx",
        "text": 'Dean of Students',
    },
    {
        "title": 'College Search Guide paragraph 220',
        "source": "College_Search_Guide(1).docx",
        "text": 'Peabody HallP.O. Box 400708Charlottesville, VA 22904Phone: 434-924-8900',
    },
    {
        "title": 'College Search Guide paragraph 221',
        "source": "College_Search_Guide(1).docx",
        "text": 'Education Abroad',
    },
    {
        "title": 'College Search Guide paragraph 222',
        "source": "College_Search_Guide(1).docx",
        "text": '(International Studies Office)208 Minor HallP.O. Box 400165Charlottesville, VA 22904Phone: 434-982-3010',
    },
    {
        "title": 'College Search Guide paragraph 223',
        "source": "College_Search_Guide(1).docx",
        "text": 'Athletics (Virginia Athletics Communications)',
    },
    {
        "title": 'College Search Guide paragraph 224',
        "source": "College_Search_Guide(1).docx",
        "text": 'John Paul Jones Arena295 Massie RoadCharlottesville, VA 22904 (Room 154)P.O. Box 400853Phone: 434-982-5500',
    },
    {
        "title": "Campus food reputation",
        "source": "https://dining.virginia.edu/",
        "text": (
            "UVA Dining's official site says the university provides dining halls, meal plans, and nutrition resources. "
            "This project treats whether food is 'good' as subjective and answers with those official dining-program facts."
        ),
    },
    {
        "title": "SAT and ACT policy",
        "source": "https://admission.virginia.edu/admission/deadlines-instructions",
        "text": (
            "UVA uses a test-optional first-year admissions policy, so SAT or ACT scores are optional rather than required "
            "for applicants in the covered admission cycles."
        ),
    },
    {
        "title": "Financial aid and admissions",
        "source": "https://sfs.virginia.edu/financial-aid-new-applicants",
        "text": (
            "UVA financial aid is related to a student's demonstrated financial need. For U.S. citizens and permanent residents, "
            "UVA states admissions are need-blind, meaning ability to pay is not used in the admission decision."
        ),
    },
]

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "what",
    "where",
    "who",
}


def _tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


def _term_freq(tokens: List[str]) -> Dict[str, float]:
    if not tokens:
        return {}
    counts: Dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    total = float(len(tokens))
    return {term: count / total for term, count in counts.items()}


def _cosine_sim(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(value * vec_b.get(term, 0.0) for term, value in vec_a.items())
    norm_a = math.sqrt(sum(value * value for value in vec_a.values()))
    norm_b = math.sqrt(sum(value * value for value in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _rank_knowledge(question: str, top_k: int = 3) -> List[Dict[str, str]]:
    q_tokens = _tokenize(question)
    q_vec = _term_freq(q_tokens)
    q_set = set(q_tokens)
    scored: List[Tuple[float, Dict[str, str]]] = []
    for doc in UVA_KNOWLEDGE:
        d_tokens = _tokenize(doc["title"] + " " + doc["text"])
        d_vec = _term_freq(d_tokens)
        overlap = len(q_set.intersection(set(d_tokens)))
        score = float(overlap) + (_cosine_sim(q_vec, d_vec) / 100.0)
        scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


def _http_json(url: str, payload: Dict) -> Dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _choose_model() -> str:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        available = [m.get("name", "") for m in payload.get("models", []) if m.get("name")]
        if not available:
            return PREFERRED_MODELS[0]
        for preferred in PREFERRED_MODELS:
            for model in available:
                if model == preferred or model.startswith(preferred + ":"):
                    return model
        return available[0]
    except Exception:
        return PREFERRED_MODELS[0]


def _build_prompt(question: str, context_docs: List[Dict[str, str]]) -> str:
    context = "\n\n".join(
        f"[{idx+1}] {doc['title']}\nSource: {doc['source']}\n{doc['text']}"
        for idx, doc in enumerate(context_docs)
    )
    return (
        "You are a factual UVA information assistant. Use only the provided context. "
        "If context is insufficient, say so briefly.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        "Answer concisely and include source numbers you used (like [1], [2])."
    )


def _generate_with_ollama(question: str, context_docs: List[Dict[str, str]]) -> Tuple[str, str]:
    prompt = _build_prompt(question, context_docs)
    model = _choose_model()
    try:
        payload = {"model": model, "prompt": prompt, "stream": False}
        response = _http_json(f"{OLLAMA_URL}/api/generate", payload)
        answer = (response.get("response") or "").strip()
        if answer:
            return answer, model
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        pass

    fallback = " ".join(f"[{i+1}] {doc['text']}" for i, doc in enumerate(context_docs))
    return f"Ollama unavailable. Retrieved UVA context: {fallback}", model


def answer_question(question: str) -> Dict:
    question = (question or "").strip()
    if not question:
        return {"error": "Question cannot be empty."}

    context_docs = _rank_knowledge(question)
    answer, model = _generate_with_ollama(question, context_docs)
    return {
        "question": question,
        "answer": answer,
        "model": model,
        "sources": [{"title": d["title"], "source": d["source"]} for d in context_docs],
    }


class RAGRequestHandler(BaseHTTPRequestHandler):
    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: Dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            self._send_html(
                """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>UVA RAG</title>
</head>
<body>
  <h1>UVA RAG</h1>
  <p>Ask a question about UVA.</p>
  <label for="question">Question</label><br />
  <textarea id="question" rows="4" cols="60" placeholder="Type your question..."></textarea><br />
  <button id="askBtn" type="button" aria-label="Submit question">Ask</button>
  <pre id="result"></pre>
  <script>
    const button = document.getElementById("askBtn");
    const questionInput = document.getElementById("question");
    const result = document.getElementById("result");
    button.addEventListener("click", async () => {
      result.textContent = "Loading...";
      try {
        const response = await fetch("/ask", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({question: questionInput.value})
        });
        const data = await response.json();
        if (!response.ok) {
          result.textContent = "Error " + response.status + ": " + (data.error || "Request failed.");
          return;
        }
        result.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        result.textContent = "Request failed: " + (err?.message || "Unknown error");
      }
    });
  </script>
</body>
</html>"""
            )
            return
        if self.path == "/health":
            self._send_json({"status": "ok", "service": "uva-rag", "port": PORT})
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/ask":
            self._send_json({"error": "Not found"}, status=404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > MAX_REQUEST_BYTES:
            self._send_json({"error": "Payload too large."}, status=413)
            return
        raw = self.rfile.read(content_length) if content_length > 0 else b""

        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body."}, status=400)
            return

        result = answer_question(str(payload.get("question", "")))
        if "error" in result:
            self._send_json(result, status=400)
            return
        self._send_json(result)

    def log_message(self, msg_format: str, *args) -> None:
        return


def run_server() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), RAGRequestHandler)
    print(f"UVA RAG server running on http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
