import { Octokit } from "octokit";

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN // optional: needed if you want private repos
});

async function repos() {
  const response = await octokit.request("GET /orgs/{org}/repos", {
    org: "nulib-ds",
    type: "all",
    per_page: 100
  });
  return response.data;
}

repos().then(data => {
  console.log(data); // prints array of repo objects
});
