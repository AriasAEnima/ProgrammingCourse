const devs = [
  {
    name: "Eduardo",
    lastName: "Arias",
    age: 28,
    contactInfo: {
      phone: 3000000,
      email: "julianeduardoarias@outlook.com",
    },
    experience: {
      languages: ["Python", "Scala", "Clojure", "Java"],
    },
  },
];

const createContactInfo = (phone, email) => { return { phone , email } };
const createExperience = (languages, tecnologies) => { return {languages, tecnologies}};

function createDev(name, lastName, age, phone, email, languages, tecnologies) {
  // More code here
  return {
    name,
    lastName,
    age,
    contactInfo: createContactInfo(phone, email),
    experience: createExperience(languages, tecnologies )
  };
}

devs.push(createDev("Camilo", "Ballesteros", "30", "23123", "c@b.com", ["C#"], ["AWS"]))

console.log(JSON.stringify(devs, null, 4));

function getDevByNameAndEmail(devName, devEmail) {
  const results = [];
  for (const dev of devs) {
    const { name, contactInfo } = dev;
    if (devName == name && devEmail == contactInfo.email) {
      results.push(dev);
    }
  }
  return results;
}

const devFound = getDevByNameAndEmail(
  "Camilo",
  "c@b.com"
);
 console.log("Dev found:", devFound);
