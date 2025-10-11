import azure.functions as func
import logging
from test_utils import MockTimer
from test_utils import MockOut
from test_utils import MockIn

def test_get_bearer_token(entry):
    """ This example shows how test case works. """
    # Call the function.
    resp = entry.livehire_api_authentication._get_bearer_token()
    logging.info(resp['body'].get('access_token'))
    # Check the output.
    assert(resp['status_code'] == 200)
    assert(resp['body'] is not None)
    assert(resp['body'].get('access_token') is not None)
    assert(resp['body'].get('expires_in') > 3000)
    assert(resp['body'].get('token_type') == 'Bearer')

def test_func_livehire_main(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_main.build().get_user_function()
    req = MockTimer()
    queuestr = MockOut()
    blobstr = MockOut()
    _ = func_call(req, 
                  queuestr, queuestr, queuestr, queuestr, queuestr, queuestr, queuestr, queuestr, queuestr, queuestr, 
                  blobstr)
    # Check the output.
    assert(queuestr.val)
    assert(blobstr.val)

def test_func_livehire_api_export_analytics_activities(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_activities.build().get_user_function()
    req = MockIn('002')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"ActivityId","ActivityTimeStamp","ActivityDate","Activity Category","Activity Type","ConnectedProfileId","JobVacancyUuid","JobCandidateUuid","JobOfferUuid","MovedToJobCandidateStatusId"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_job_vacancies(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_job_vacancies.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"JobVacancyUuid","Job Id","Collaborators","Segment","Recruitment Process","Job Title","Url Code","Expression of Interest","Desired Start Date","Target Days to Hire","JobLocationId","Country","State","Postcode","Suburb","Work Type","Contract Duration","Minimum Remuneration","Maximum Remuneration","Remuneration Package","Internal Notes","Category","SubCategory","Cost Centre","Job Status","Positions","Filled Positions","Unfilled Positions","Days Open","Job Opened Date","Job Closed Date","Job Closed Reason","Job Closed Reason Detail","JobHiringManagerId","JobRecruiterId"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_job_vacancies_additional_fields(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_job_vacancies_additional_fields.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"JobVacancyUuid","JobVacancyID","CostCentre","Furtherinfo","Languages","Name","Languagestwo","Comments","Details","AdditionalDetails","ReportingManager","Facility","DaysTimes","Competency","Projectacg","Project","Active","Programtwo","Program","Programtwoacg","Gender","Gendertwo","Brand","Modality","Brandact","Car","Industry","WorkingWeek","NSWRegion","SiteNSWMetro","SiteVicEast","SiteVicNorth","SiteWA","SiteNswnorth","SiteQLD","SiteVicMetro","FillPriorityACG","Modalityacg","RPOacg","SiteSA","ACTRegion","Video Interview Template","VICRegion","PositionType","HiringCompany","RPO","FillPriority","JobState","Site","ExpLevel","Job","Department","Division","Pets","Children","Areas","Checks","ForcedAgency","ForcedAgencyacg","Vid Req","AutoInvite","AgencyRequired","Locum","sleepovers","DriversLicense","Hours","Internal","Limtedreg","Locumacg","Region","Japara","Check Template","Check Req","Hub_Names"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_hiring_managers(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_hiring_managers.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"JobHiringManagerId","Email","First Name","Last Name","Full Name","User Role"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_job_recruiters(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_job_recruiters.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"JobRecruiterId","Email","First Name","Last Name","Full Name","User Role"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_job_candidates(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_job_candidates.build().get_user_function()
    req = MockIn('002')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"ConnectedProfileId","JobCandidateUuid","JobCandidateCurrentStatusId","Candidate Status","Candidate Base Status","Ordered Candidate Status","Is From Talent Pool","Days To Hire","Application Date","StatusLastChangedAt","NotSuitableStatusAt","Unsuccessful","Unsuccessful Notification Status","Days From Marked Unsuccessful to Unsuccessful Notification","Days From Application to Unsuccessful Notification","Filled by Target","Days From Application To Hire","Candidate Source","Candidate Source Group","Rehire","AlreadyInTC"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_job_candidate_status(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_job_candidate_status.build().get_user_function()
    req = MockIn('002')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"ActivityId","JobCandidateId","ActivityTimeStamp","ActivityDate","Updated Candidate Status","Sequence","Updated Candidate Status (Standard)"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_job_offers(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_job_offers.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"JobOfferUuid","Job Offer Status","Recruitment Method","Commencement Date","Remuneration Amount","Remuneration Currency","Remuneration Type","Remuneration Type Group","Remuneration Amount (Clean)","Remuneration Salary (Range)","Remuneration Hourly Rate (Range)","Remuneration Daily Rate (Range)","Company or Agency Name","Work Type"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_job_offer_additional_fields(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_job_offer_additional_fields.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)
    # Check the output.
    expected_schema = '"JobOfferUuid","JobOfferId","startdateconfirmed","employingentity","reportstoname","reportstoposition","hoursofwork","award","awardlevel","workerscreeningcompleted","salaryband","category","otherbenefits","workeligibility","otherbenefitsother","rpo","SourceOfHire","visatype","Limtedreg","OSLimtedreg","Locum","OSLimtedregACG","LocumACG","LimtedregACG","Divisions","Templates"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

def test_func_livehire_api_export_analytics_profiles(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_api_export_analytics_profiles.build().get_user_function()
    req = MockIn('002')
    blobstr = MockOut()
    queuestr = MockOut()
    inputblob = 'mock_bearer_token'
    _ = func_call(blobstr, queuestr, req, inputblob)                                                                              
    # Check the output.
    expected_schema = '"ConnectedProfileId","Year of Birth","Age (Group)","ATSI","Desired Salary","Desired Salary Range","Years of Experience","Willing to Relocate","Current Job Title","Temporary Profile","Profile Strength","Profile Completion","Preferred Work Types","Full Name","Australian Citizen or Permanent Resident","Connection Status","Rating","Relationship","Pipeline Status","Gender","Availability","Notice Period","Country","State","Suburb","Postcode","Application Count","Application Count (Group)","Application Volume"'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.splitlines()[0] == expected_schema)

# def test_example_case(entry):
#     """ This example shows how test case works. """
#     # Construct a mock HTTP request.
#     req = func.HttpRequest(method='GET',
#                            body=None,
#                            url='/api/func_http_trigger',
#                            params={'value': '21'})
#     # Call the function.
#     func_call = entry.func_http_trigger.build().get_user_function()
#     resp = func_call(req)
#     # Check the output.
#     assert(
#         resp.get_body() == b'21 * 2 = 42'
#     )