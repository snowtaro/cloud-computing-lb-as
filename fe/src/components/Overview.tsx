const Overview = () => {
  return (
    <div className="flex flex-col space-y-8 items-center">
      <iframe
        src="http://localhost:3001/d-solo/b13ea432-f40d-4f78-8a44-232d990877b0/pnu-cloud-computing?orgId=1&from=now-5m&to=now&timezone=browser&refresh=5s&panelId=1&__feature.dashboardSceneSolo"
        className="w-full max-w-4xl h-64 border-none rounded"
        title="HTTP 요청량"
      />
      <iframe
        src="http://localhost:3001/d-solo/b13ea432-f40d-4f78-8a44-232d990877b0/pnu-cloud-computing?orgId=1&from=now-5m&to=now&timezone=browser&refresh=5s&panelId=3&__feature.dashboardSceneSolo"
        className="w-full max-w-4xl h-64 border-none rounded"
        title="CPU 사용량"
      />
      <iframe
        src="http://localhost:3001/d-solo/b13ea432-f40d-4f78-8a44-232d990877b0/pnu-cloud-computing?orgId=1&from=now-5m&to=now&timezone=browser&refresh=5s&panelId=2&__feature.dashboardSceneSolo"
        className="w-full max-w-4xl h-64 border-none rounded"
        title="서버 수"
      />
    </div>
  );
};

export default Overview;
