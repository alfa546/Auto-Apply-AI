import os

dest_file = 'frontend/src/app/components/Dashboard.tsx'

with open(dest_file, 'r', encoding='utf-8') as f:
    content = f.read()

idx1 = content.find('return (\n    <div className="min-h-screen')
if idx1 == -1:
    idx1 = content.find('return (\n    <div className=\\"min-h-screen')

imports = """import JobsTab from "./JobsTab";
import HistoryTab from "./HistoryTab";
import ProfileTab from "./ProfileTab";
import SettingsTab from "./SettingsTab";
import GmailModal from "./GmailModal";
import Toast from "./Toast";
import { DashboardIcon, GmailIcon, UserIcon, CheckCircleIcon, KeyIcon } from "./Icons";
import { Job, Application, ProfileData, AtsMetrics } from "../types";
import { ALL_WORLD_COUNTRIES } from "../constants";
"""

new_return = """return (
    <div className="min-h-screen bg-[#090a0f] bg-grid-omni bg-coral-glow text-slate-100 font-sans selection:bg-rose-500 selection:text-white">
      {notification && (
        <Toast notification={notification} />
      )}

      <header className="border-b border-white/10 bg-[#090a0f]/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 bg-rose-500 transform rotate-45 rounded-sm shadow-[0_0_12px_rgba(244,63,94,0.8)]"></div>
            <h1 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
              AutoApply<span className="text-rose-500 font-normal">AI</span>
            </h1>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <button onClick={() => setActiveTab("jobs")} className={`hover:text-white transition-colors ${activeTab === "jobs" ? "text-rose-400 font-semibold" : ""}`}>
              Opportunities
            </button>
            <button onClick={() => setActiveTab("history")} className={`hover:text-white transition-colors ${activeTab === "history" ? "text-rose-400 font-semibold" : ""}`}>
              Gmail Proofs
            </button>
            <button onClick={() => setActiveTab("profile")} className={`hover:text-white transition-colors ${activeTab === "profile" ? "text-rose-400 font-semibold" : ""}`}>
              CV & Profile
            </button>
            <button onClick={() => setActiveTab("settings")} className={`hover:text-white transition-colors ${activeTab === "settings" ? "text-rose-400 font-semibold" : ""}`}>
              API Vault
            </button>
          </nav>

          <div className="flex items-center gap-3">
            {isGmailConnected && (
              <div className="hidden sm:flex items-center gap-2 bg-rose-950/40 border border-rose-500/30 px-3.5 py-1.5 rounded-full text-xs text-rose-300">
                <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping"></span>
                <span>Gmail: <strong className="text-rose-200">{gmailEmail}</strong></span>
              </div>
            )}
            <button onClick={() => setActiveTab("settings")} className="btn-red-glow text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-2">
              <KeyIcon />
              <span>API Vault</span>
              <span>→</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex border-b border-white/10 mb-8 overflow-x-auto gap-2">
          <button onClick={() => setActiveTab("jobs")} className={`pb-3.5 px-6 font-semibold text-sm border-b-2 whitespace-nowrap transition-all flex items-center gap-2.5 rounded-t-xl ${activeTab === "jobs" ? "border-rose-400 text-rose-300 bg-rose-950/20 shadow-[0_4px_20px_-4px_rgba(244,63,94,0.3)]" : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"}`}>
            <DashboardIcon />
            <span>Daily Opportunities</span>
            <span className="ml-1 bg-rose-950/80 text-rose-300 text-xs px-2.5 py-0.5 rounded-full border border-rose-500/30 font-mono">
              {filteredDailyJobs.length}
            </span>
          </button>
          <button onClick={() => setActiveTab("history")} className={`pb-3.5 px-6 font-semibold text-sm border-b-2 whitespace-nowrap transition-all flex items-center gap-2.5 rounded-t-xl ${activeTab === "history" ? "border-rose-400 text-rose-300 bg-rose-950/20 shadow-[0_4px_20px_-4px_rgba(244,63,94,0.3)]" : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"}`}>
            <GmailIcon />
            <span>Applications & Gmail Proofs</span>
            <span className="ml-1 bg-rose-950/80 text-rose-300 border border-rose-500/30 text-xs px-2.5 py-0.5 rounded-full font-mono">
              {applications.length}
            </span>
          </button>
          <button onClick={() => setActiveTab("profile")} className={`pb-3.5 px-6 font-semibold text-sm border-b-2 whitespace-nowrap transition-all flex items-center gap-2.5 rounded-t-xl ${activeTab === "profile" ? "border-rose-400 text-rose-300 bg-rose-950/20 shadow-[0_4px_20px_-4px_rgba(244,63,94,0.3)]" : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"}`}>
            <UserIcon />
            <span>User Profile & CV Management</span>
          </button>
        </div>

        {activeTab === "jobs" && (
          <JobsTab
            filteredDailyJobs={filteredDailyJobs}
            selectedCountries={selectedCountries}
            isTriggeringSearch={isTriggeringSearch}
            handleTriggerSearchAgent={handleTriggerSearchAgent}
            isApplyingId={isApplyingId}
            handleAutoApply={handleAutoApply}
          />
        )}
        {activeTab === "profile" && (
          <ProfileTab
            userEmail={userEmail}
            setUserEmail={setUserEmail}
            portfolioUrl={portfolioUrl}
            setPortfolioUrl={setPortfolioUrl}
            githubUrl={githubUrl}
            setGithubUrl={setGithubUrl}
            otherUrl={otherUrl}
            setOtherUrl={setOtherUrl}
            targetRoles={targetRoles}
            setTargetRoles={setTargetRoles}
            countryQuery={countryQuery}
            setCountryQuery={setCountryQuery}
            isCountryDropdownOpen={isCountryDropdownOpen}
            setIsCountryDropdownOpen={setIsCountryDropdownOpen}
            selectedCountries={selectedCountries}
            handleSelectCountryFromDropdown={handleSelectCountryFromDropdown}
            handleRemoveCountry={handleRemoveCountry}
            workModePref={workModePref}
            setWorkModePref={setWorkModePref}
            salaryPref={salaryPref}
            setSalaryPref={setSalaryPref}
            experiencePref={experiencePref}
            setExperiencePref={setExperiencePref}
            visaSponsorshipPref={visaSponsorshipPref}
            setVisaSponsorshipPref={setVisaSponsorshipPref}
            selectedEmpTypes={selectedEmpTypes}
            toggleEmpType={toggleEmpType}
            dailyJobGoal={dailyJobGoal}
            setDailyJobGoal={setDailyJobGoal}
            dailyInternshipGoal={dailyInternshipGoal}
            setDailyInternshipGoal={setDailyInternshipGoal}
            totalTodayApplied={totalTodayApplied}
            totalDailyTarget={totalDailyTarget}
            overallGoalProgress={overallGoalProgress}
            todayJobsCount={todayJobsCount}
            todayInternshipsCount={todayInternshipsCount}
            isSavingProfile={isSavingProfile}
            handleSaveProfile={handleSaveProfile}
            isUploading={isUploading}
            agentPhase={agentPhase}
            agentLogs={agentLogs}
            uploadedResume={uploadedResume}
            handleResumeUpload={handleResumeUpload}
            extractedProfile={extractedProfile}
            atsMetrics={atsMetrics}
            handleRunAtsCheck={handleRunAtsCheck}
            isAnalyzingATS={isAnalyzingATS}
          />
        )}
        {activeTab === "history" && (
          <HistoryTab
            historyFilter={historyFilter}
            setHistoryFilter={setHistoryFilter}
            todayApps={todayApps}
            todayJobsCount={todayJobsCount}
            todayInternshipsCount={todayInternshipsCount}
            monthlyApps={monthlyApps}
            yearlyApps={yearlyApps}
            applications={applications}
            filteredApplications={filteredApplications}
          />
        )}
        {activeTab === "settings" && (
          <SettingsTab
            showApiKeys={showApiKeys}
            setShowApiKeys={setShowApiKeys}
            llmProvider={llmProvider}
            setLlmProvider={setLlmProvider}
            llmModel={llmModel}
            setLlmModel={setLlmModel}
            customApiBase={customApiBase}
            setCustomApiBase={setCustomApiBase}
            openaiApiKey={openaiApiKey}
            setOpenaiApiKey={setOpenaiApiKey}
            googleClientId={googleClientId}
            setGoogleClientId={setGoogleClientId}
            googleClientSecret={googleClientSecret}
            setGoogleClientSecret={setGoogleClientSecret}
            isGmailConnected={isGmailConnected}
            gmailEmail={gmailEmail}
            setShowGmailModal={setShowGmailModal}
            adzunaAppId={adzunaAppId}
            setAdzunaAppId={setAdzunaAppId}
            adzunaAppKey={adzunaAppKey}
            setAdzunaAppKey={setAdzunaAppKey}
            joobleApiKey={joobleApiKey}
            setJoobleApiKey={setJoobleApiKey}
            isSavingApiSettings={isSavingApiSettings}
            handleSaveApiSettings={handleSaveApiSettings}
          />
        )}
      </main>

      {showGmailModal && (
        <GmailModal
          gmailEmail={gmailEmail}
          setGmailEmail={setGmailEmail}
          smtpPassword={smtpPassword}
          setSmtpPassword={setSmtpPassword}
          setShowGmailModal={setShowGmailModal}
          setIsGmailConnected={setIsGmailConnected}
          showToast={showToast}
          username={username}
        />
      )}
    </div>
  );
}
"""

if idx1 != -1:
    new_content = imports + '\n' + content[:idx1] + new_return
    with open(dest_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
else:
    print("Could not find return statement")
