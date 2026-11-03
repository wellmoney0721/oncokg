import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/'audit_evidence_round3'
sys.path.insert(0,str(ROOT/'src'))
import normalize as N,textrules as T

# Every current key is included. A historical closing is NOT evidence that the
# subsidiary remains a separate extant legal entity in November 2026.
groups={
'Roche':('GROUP_AFFILIATION_SUPPORTED','https://www.roche.com/our-websites','Current group websites identify Genentech and Chugai as group members.'),
'Merck & Co':('AFFILIATION_SUPPORTED_LEGAL_IDENTITY_NOT_FULLY_VERIFIED','https://www.msd.com/news/msd-completes-acquisition-of-prometheus-biosciences-inc/','Prometheus acquisition closed June 2023. MSD is explicitly a tradename of Merck & Co, not necessarily a separate legal company.'),
'Merck KGaA':('GROUP_AFFILIATION_SUPPORTED','https://www.reports.emdgroup.com/en/annualreport/2025/notes/scope-of-consolidation/list-of-shareholdings.html','2025 shareholding list supports Merck Serono and EMD group affiliation; unqualified division/brand names do not identify one separate legal entity.'),
'Bristol Myers Squibb':('ACQUISITIONS_SUPPORTED_CURRENT_LEGAL_EXISTENCE_NOT_ALL_VERIFIED','https://www.bms.com/our-company/partnerships-and-business-development/existing-partners.html','Current corporate history lists closing of Mirati and RayzeBio and Turning Point acquisition. Separate legal persistence is not established for every acquired name.'),
'AstraZeneca':('ACQUISITIONS_SUPPORTED_CURRENT_LEGAL_EXISTENCE_NOT_ALL_VERIFIED','https://www.astrazeneca.com/our-company/history.html','Current corporate history supports MedImmune and Alexion acquisition. It does not establish separate current legal status for all named subsidiaries.'),
'Eli Lilly':('IDENTITY_OR_ACQUISITION_SUPPORTED','https://investor.lilly.com/node/40671','Loxo acquisition closed in February 2019; continued separate legal existence not established by closing release alone.'),
'Pfizer':('ACQUISITIONS_SUPPORTED_CURRENT_LEGAL_EXISTENCE_NOT_ALL_VERIFIED','https://www.pfizer.com/about/history','Pfizer current corporate history and closing releases support Wyeth, Array and Seagen acquisition. Separate legal persistence not established for every acquired name.'),
'Novartis':('CURRENT_IDENTITY_SUPPORTED','https://www.novartis.com/about','Exact key is a self-map, so no parent edge is created for the exact name.'),
'Sanofi':('ACQUISITIONS_SUPPORTED_CURRENT_LEGAL_EXISTENCE_NOT_ALL_VERIFIED','https://www.sanofi.de/de/unternehmen/historie','Corporate history supports Aventis and Genzyme acquisitions; continuing separate legal existence is not proven by acquisition history.'),
'Takeda':('ACQUISITIONS_SUPPORTED_CURRENT_LEGAL_EXISTENCE_NOT_ALL_VERIFIED','https://www.takeda.com/about/our-company/history/','Current history supports Millennium integration; ARIAD closing release confirms February 2017 acquisition, not current independent legal persistence.'),
'Boehringer Ingelheim':('CURRENT_IDENTITY_SUPPORTED','https://www.boehringer-ingelheim.com/science-innovation/human-health-innovation?page=8','Current corporate material identifies the company as family owned. Exact key self-maps.'),
'Johnson & Johnson':('GROUP_AFFILIATION_SUPPORTED','https://www.investor.jnj.com/investor-news/news-details/2023/Johnson--Johnson-Marks-New-Era-as-Global-Healthcare-Company-With-Updated-Visual-Identity/default.aspx','Janssen is the pharmaceutical segment; rebranding to Johnson & Johnson Innovative Medicine announced September 2023. Bare Janssen is not proof of one specific extant legal entity.'),
'GSK':('WRONG_RELATION_RENAME_NOT_OWNERSHIP','https://find-and-update.company-information.service.gov.uk/company/03888792/filing-history?page=12','GlaxoSmithKline plc became GSK plc in May 2022. Code nevertheless creates live GSK PARENT_OF GlaxoSmithKline.'),
'Amgen':('CURRENT_IDENTITY_SUPPORTED','https://www.amgen.com/about','Exact key self-maps; current company identity supported.'),
'Bayer':('CURRENT_IDENTITY_SUPPORTED','https://www.bayer.com/en','Exact key self-maps; prefix application is unsafe, e.g. Bayerische Motoren Werke AG gets Bayer as parent.'),
'Daiichi Sankyo':('CURRENT_IDENTITY_SUPPORTED','https://www.daiichisankyo.com/about_us/mission-strength/history/index.html','Daiichi Sankyo current identity supported; predecessor Daiichi Pharmaceutical separately assessed below.'),
'Eisai':('CURRENT_LEGAL_STATUS_UNVERIFIED','https://www.eisai.com/company/profile/index.html','Official profile returned HTTP 403. Exact key self-maps. No current legal-status verification claimed.'),
'BeOne Medicines':('RENAME_VERIFIED','https://sseir.beonemedicines.com/en/news/beone-medicines-launches-following-redomiciliation-to-switzerland-marking-a-new-chapter-in-global-oncology/3bf1505f-9411-4a38-b445-54544ad4c88e','BeiGene name change and Swiss continuation took effect May 27 2025; same-entity treatment is supported.'),
'Jiangsu Hengrui':('CURRENT_IDENTITY_SUPPORTED','https://www.hengrui.com/en/media/detail-929.html','Current official name is Jiangsu Hengrui Pharmaceuticals Co., Ltd.; adding Medicine after normalized key creates an artificial parent-child split in this snapshot.'),
'Innovent':('CURRENT_IDENTITY_SUPPORTED','https://en.innoventbio.com/InvestorsAndMedia/PressReleaseDetail?key=612','Official August 2026 release calls Innovent Biologics, Inc. Innovent; graph nevertheless has Innovent PARENT_OF Innovent Biologics.'),
'Junshi':('CURRENT_IDENTITY_SUPPORTED','https://www.junshipharma.com/en/about-us/','Current corporate about page supports Junshi Biosciences; exact key is a self-map.'),
'Yuhan':('CURRENT_IDENTITY_SUPPORTED','https://www.yuhan.co.kr/Mobile/Invest/ControlStructure/ArticlesOfIncorporation2/','March 2025 articles identify English legal name Yuhan Corporation; exact key self-maps.'),
'Hanmi':('CURRENT_IDENTITY_SUPPORTED','https://englishdart.fss.or.kr/dsbc001/selectPopup.ax?selectKey=00828497','Korean regulator issuer profile supports Hanmi Pharm.; bare Hanmi is ambiguous outside the pharma domain.'),
}
extra={
'scheringplough':('WRONG_RELATION_SURVIVING_ENTITY_RENAMED','https://www.sec.gov/Archives/edgar/data/310158/000119312512084319/R10.htm','SEC merger note says Schering-Plough was the surviving public company renamed Merck & Co in November 2009; old Merck became subsidiary MSD. PARENT_OF mistakes rename/history for current ownership.'),
'mercksharpdohme':('CURRENT_SUBSIDIARY_SUPPORTED','https://www.merck.com/terms-of-use/','Current terms revised March 2025 identify Merck Sharp & Dohme LLC as a subsidiary of Merck & Co.'),
'merckcoinc':('SAME_COMPANY_ALIAS_NOT_OWNERSHIP','https://www.merck.com/terms-of-use/','Name refers to Merck & Co itself; real input loses legal suffixes and produces key merck, so this map key is not reached for Merck & Co., Inc.'),
'turningpoint':('CLOSING_VERIFIED_CURRENT_LEGAL_STATUS_UNVERIFIED','https://news.bms.com/news/details/2022/Bristol-Myers-Squibb-Completes-Acquisition-of-Turning-Point-Therapeutics-Expanding-Precision-Oncology-Portfolio/default.aspx','Acquisition closed August 17 2022; closing release alone does not establish November 2026 legal persistence.'),
'merckhealthcarekgaa':('GROUP_AFFILIATION_SUPPORTED_CURRENT_LEGAL_STATUS_NOT_FULLY_VERIFIED','https://www.emdgroup.com/content/dam/web/corporate/non-images/company/responsibility/us/regulations-and-guidelines/Certificate-ISO-50001-2018-DE.pdf','Official November 2025 group certificate names Merck Healthcare KGaA; separate legal persistence in November 2026 not independently checked.'),
'acerta':('CURRENT_GROUP_MEMBERSHIP_AND_CLOSING_VERIFIED','https://www.acerta-pharma.com/about.html','Acerta current site says member of AstraZeneca Group, acquisition of remaining stake completed in 2021.'),
'celgene':('CURRENT_GROUP_MEMBERSHIP_SUPPORTED','https://www.dailymed.nlm.nih.gov/dailymed/getFile.cfm?setid=594bb413-af3b-4b97-afb3-bfe2b174f2ed','December 2025 label names Celgene Corporation as a Bristol-Myers Squibb company.'),
'juno':('CURRENT_GROUP_MEMBERSHIP_SUPPORTED','https://www.hkexnews.hk/listedco/listconews/sehk/2026/0428/2026042800271.pdf','2025 audited annual report states Juno wholly owned by Celgene, in turn wholly owned by BMS. PARENT_OF here skips an ownership level.'),
'mirati':('CLOSING_VERIFIED_CURRENT_LEGAL_STATUS_UNVERIFIED','https://investors.bms.com/iframes/press-releases/press-release-details/2024/Bristol-Myers-Squibb-Completes-Acquisition-of-Mirati-Therapeutics-Strengthening-and-Diversifying-Oncology-Portfolio/default.aspx','Acquisition closed January 23 2024; release alone does not establish continuing separate legal entity in November 2026.'),
'rayzebio':('CLOSING_VERIFIED_CURRENT_LEGAL_STATUS_UNVERIFIED','https://news.bms.com/news/details/2024/Bristol-Myers-Squibb-Completes-Acquisition-of-RayzeBio-Adding-Differentiated-Actinium-Based-Radiopharmaceutical-Platform/default.aspx','Acquisition closed February 26 2024; release alone does not establish current separate legal entity.'),
'alexion':('CLOSING_VERIFIED_CURRENT_LEGAL_STATUS_UNVERIFIED','https://www.astrazeneca.com/media-centre/press-releases/2021/acquisition-of-alexion-completed.html','Acquisition closed July 2021; continued separate legal status not verified here.'),
'array':('CLOSING_VERIFIED_PREFIX_UNSAFE','https://www.pfizer.com/news/press-release/press-release-detail/pfizer_completes_acquisition_of_array_biopharma','Array BioPharma acquisition closed July 30 2019. Source comment says exact match only but key length 5 permits prefix matching at normalize.py:1124.'),
'seagen':('CLOSING_VERIFIED_CURRENT_LEGAL_STATUS_UNVERIFIED','https://www.pfizer.com/news/press-release/press-release-detail/pfizer-completes-acquisition-seagen','Acquisition closed December 14 2023; legal persistence beyond closing not established.'),
'wyeth':('CLOSING_VERIFIED_CURRENT_LEGAL_STATUS_UNVERIFIED','https://cdn.pfizer.com/pfizercom/news/press_releases/2009/pfizer_wyeth_acquisition_101509.pdf','Acquisition closed October 15 2009; current separate legal entity not established.'),
'ariad':('CLOSING_VERIFIED_CURRENT_LEGAL_STATUS_UNVERIFIED','https://www.takedaoncology.com/newsroom/news-releases/2017/ariad-acquisition-complete/','Acquisition closed February 16 2017; current separate legal entity not established.'),
'daiichi':('STALE_ENTITY_DISSOLVED','https://www.daiichisankyo.com/files/news/pressrelease/pdf/005511/news2009_05_28_191_en.pdf','Consolidated financial statements record Daiichi Pharmaceutical dissolved in merger April 1 2007. Live parent-child graph relation is not a current ownership relation.'),
'msd':('TRADE_NAME_NOT_SEPARATE_ENTITY','https://www.msd.com/news/msd-completes-acquisition-of-prometheus-biosciences-inc/','MSD is explicitly the tradename of Merck & Co. A bare MSD parent-child edge asserts a legal distinction not supplied by this evidence.'),
'merckshampdohme':('UNVERIFIED_MISSPELLED_ALIAS',None,'No corporate primary source found for this exact spelling; intended Merck Sharp & Dohme identity inferred from code only.'),
'merckshapdohme':('UNVERIFIED_MISSPELLED_ALIAS',None,'No corporate primary source found for this exact spelling; intended Merck Sharp & Dohme identity inferred from code only.'),
'merckshampdohmellc':('UNVERIFIED_MISSPELLED_ALIAS',None,'No corporate primary source found for this exact spelling; intended Merck Sharp & Dohme identity inferred from code only.'),
}
tree=ast.parse((ROOT/'src/normalize.py').read_text(encoding='utf8'))
lines={}
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CURATED_PARENTS' for t in node.targets):
  lines={k.value:k.lineno for k in node.value.keys}
entries=[]
for key,parent in N.CURATED_PARENTS.items():
 status,url,note=extra.get(key,groups[parent])
 entries.append({'key':key,'parent':parent,'source_line':f'src/normalize.py:{lines[key]}','status':status,'evidence_url':url,'note':note,'exact_key_is_self_map':key==T.canonical_key(parent)})
result={'audited_on':'2026-11-03','scope':'Every key in current CURATED_PARENTS; historical acquisition support is separated from current legal persistence. Prefix matches over all possible company names are not verified by a correct exact-key mapping.','actual_key_count':len(entries),'readme_claim':{'file_line':'README.md:457','claimed':59,'actual':len(entries),'status':'MISMATCH'},'entries':entries,'negative_checks':[{'name':'Sandoz','code_status':'absent from parent map','status':'REPAIR_SUPPORTED','source':'https://ar.sandoz.com/Sandoz_2025_annual_report.pdf','evidence':'2025 report identifies second full year as independent public company.'}],'probe_evidence':'graph_company_probes.json','live_edge_evidence':'graph_additional_snapshot_checks.json'}
(OUT/'graph_corporate_map_review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
print('reviewed',len(entries),'keys')
