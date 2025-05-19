from enum import Enum

class SheetName(Enum):
	LOCATION="Location"
	LOCATIONGROUP="LocationGroup"
	LOCATIONLEGALENTITY="LocationLegalEntity"
	LOCATIONAREA="LocationArea"
	LOCATIONAREAHISTORY="LocationAreaHistory"
	LOCATIONTOPARTNER="LocationToPartner"
	LOCATIONTOPARTNERCONTACT="LocationToPartnerContact"
	OPERATINGCOSTPERIOD="OperatingCostPeriod"
	OPERATINGCOSTPERIODEXPENSE="OperatingCostPeriodExpense"
	PREMISE="Premise"
	PREMISEAREA="PremiseArea"
	PREMISEAREAHISTORY="PremiseAreaHistory"
	PREMISEGROUP="PremiseGroup"
	LEASE="Lease"
	TERMS="Terms"
	TERMAMOUNTS="TermAmounts"
	TERMVENDOR="TermVendor"
	NFSLINK="NfsLink"
	PERCENTAGERENTPERIOD="PercentageRentPeriod"
	PERCENTAGERENTEXCLUSION="PercentageRentExclusion"
	PERCENTAGERENTRULE="PercentageRentRule"
	LEASECLAUSETYPE="LeaseClauseType"
	CLAUSE="Clause"
	LEASECRITICALCLAUSETYPE="LeaseCriticalClauseType"
	CRITICALCLAUSE="CriticalClause"
	INSURANCE="Insurance"
	LEASECONDITION="LeaseCondition"
	AREABASEDPROSHARE="AreaBasedProShare"
	FIXEDPERCENTAGEPROSHARE="FixedPercentageProShare"
	FIXEDCAP="FixedCAP"
	OVERBASECAP="OverBaseCAP"
	OVERYEARCAP="OverYearCAP"
	LEASEINCENTIVE="LeaseIncentive"
	DRAW="Draw"
	USERDEFINEDFIELDS="UserDefinedFields"
	LEASEEVENT="LeaseEvent"
	DOCUMENTLINK="DocumentLink"
	NOTE="Note"
	NOTEENTITYTYPEOPTION="NoteEntityTypeOption"
	DOCUMENTENTITIES="DocumentEntities"

def get_sheet_enum(value):
    return SheetName(value)


class LocationColumns(Enum):
	LOCATIONID="LocationId"
	BUSINESSUNITID="BusinessUnitId"
	STORENUMBER="StoreNumber"
	NUMBER="Number"
	DEFAULTCURRENCY="DefaultCurrency"
	DEFAULTUNIT="DefaultUnit"
	CATEGORY="Category"
	NAME="Name"
	PROPERTYTYPE="PropertyType"
	QUALITY="Quality"
	STATUS="Status"
	TYPE="Type"
	COUNTRYCODE="CountryCode"
	COUNTRYTEXT="CountryText"
	PROVINCECODE="ProvinceCode"
	PROVINCETEXT="ProvinceText"
	CITY="City"
	DISTRICT="District"
	CIVICNUMBER="CivicNumber"
	POSTALCODE="PostalCode"
	STREET="Street"
	SUITE="Suite"
	COUNTRYCODE2="CountryCode2"
	COUNTRYTEXT2="CountryText2"
	PROVINCECODE2="ProvinceCode2"
	PROVINCETEXT2="ProvinceText2"
	CITY2="City2"
	DISTRICT2="District2"
	CIVICNUMBER2="CivicNumber2"
	POSTALCODE2="PostalCode2"
	STREET2="Street2"
	SUITE2="Suite2"

class LocationGroupColumns(Enum):
	LOCATIONID="LocationId"
	GROUP="Group"
	GROUPOPTION="GroupOption"

class LocationLegalEntityColumns(Enum):
	LOCATIONID="LocationId"
	LEGALENTITYID="LegalEntityId"
	ERPSYSTEMDISPLAYID="ErpSystemDisplayId"

class LocationAreaColumns(Enum):
	LOCATIONID="LocationId"
	AREAID="AreaId"
	TYPE="Type"
	GROSSUP="GrossUp"
	LOT="Lot"
	PROSHARETYPE="ProshareType"
	SOURCE="Source"
	TOBEMEASURED="ToBeMeasured"
	UNIT="Unit"
	VERIFIED="Verified"
	APPLICABLEEXPENSES="ApplicableExpenses"

class LocationAreaHistoryColumns(Enum):
	AREAID="AreaId"
	DETAILS="Details"
	STARTDATE="StartDate"
	ENDDATE="EndDate"
	FLOOR="Floor"
	MEASURE="Measure"
	SUITE="Suite"

class LocationToPartnerColumns(Enum):
	LOCATIONID="LocationId"
	LOCATIONTOPARTNERID="LocationToPartnerId"
	PARTNERID="PartnerId"
	PARTNERROLEID="PartnerRoleId"
	DATEFROM="DateFrom"
	DATETO="DateTo"

class LocationToPartnerContactColumns(Enum):
	LOCATIONTOPARTNERID="LocationToPartnerId"
	CONTACTID="ContactId"
	ADDRESS="Address"
	DESCRIPTION="Description"
	EMAIL="Email"
	NAME="Name"
	PHONE="Phone"
	POSITION="Position"
	FAX="Fax"
	CONTACTTYPES="ContactTypes"

class OperatingCostPeriodColumns(Enum):
	LOCATIONID="LocationId"
	OPERATINGCOSTPERIODID="OperatingCostPeriodId"
	YEAR="Year"
	STATUS="Status"

class OperatingCostPeriodExpenseColumns(Enum):
	OPERATINGCOSTPERIODID="OperatingCostPeriodId"
	EXPENSETYPE="ExpenseType"
	AMOUNT="Amount"
	REVISEDAMOUNT="RevisedAmount"
	CONSIDERREVISEDAMOUNT="ConsiderRevisedAmount"

class PremiseColumns(Enum):
	LOCATIONID="LocationId"
	PREMISEID="PremiseId"
	PARENTPREMISEID="ParentPremiseId"
	HEADPREMISE="HeadPremise"
	STATUS="Status"
	NAME="Name"
	NUMBER="Number"
	USAGE="Usage"
	LEGALENTITYID="LegalEntityId"
	COSTCENTERID="CostCenterId"
	PROFITCENTERID="ProfitCenterId"
	OPENINGDATE="OpeningDate"
	CLOSINGDATE="ClosingDate"
	EXPANSIONDATE="ExpansionDate"
	POSSESSIONDATE="PossessionDate"
	RELOCATEDATE="RelocateDate"
	VACATINGDATE="VacatingDate"
	OCCUPANCIES="Occupancies"
	DEFAULTJURISDICTIONID="DefaultJurisdictionId"

class PremiseAreaColumns(Enum):
	PREMISEID="PremiseId"
	AREAID="AreaId"
	TYPE="Type"
	CADASTER="Cadaster"
	GROSSUP="GrossUp"
	LOT="Lot"
	PROSHARETYPE="ProshareType"
	SOURCE="Source"
	TOBEMEASURE="ToBeMeasure"
	UNIT="Unit"
	VERIFIED="Verified"
	APPLICABLEEXPENSES="ApplicableExpenses"

class PremiseAreaHistoryColumns(Enum):
	AREAID="AreaId"
	DETAILS="Details"
	STARTDATE="StartDate"
	ENDDATE="EndDate"
	FLOOR="Floor"
	MEASURE="Measure"
	SUITE="Suite"

class PremiseGroupColumns(Enum):
	PREMISEID="PremiseId"
	GROUP="Group"
	GROUPOPTION="GroupOption"

class LeaseColumns(Enum):
	LEASEID="LeaseId"
	NUMBER="Number"
	PREMISEID="PremiseId"
	ORIGINALLEASEID="OriginalLeaseId"
	PARENTLEASEID="ParentLeaseId"
	TYPE="Type"
	STARTDATE="StartDate"
	ENDDATE="EndDate"
	CATEGORY="Category"
	REGISTRATIONNUMBER="RegistrationNumber"
	SCENARIO="Scenario"
	STATE="State"
	STATUS="Status"
	SIGNATUREDATE="SignatureDate"
	TERMINATINGLEASEDATE="TerminatingLeaseDate"
	INDEXATIONTYPE="IndexationType"
	CPIGLOBALCATEGORYID="CpiGlobalCategoryId"
	CURRENTINDEXLEVEL="CurrentIndexLevel"
	INDEXATIONREFERENCEDATE="IndexationReferenceDate"
	CONDITIONALINDEXATIONLEASE="ConditionalIndexationLease"
	MINIMUMPERCENTAGECHANGELEASE="MinimumPercentageChangeLease"
	MAXIMUMPERCENTAGECHANGELEASE="MaximumPercentageChangeLease"
	INDEXATIONTYPENONLEASE="IndexationTypeNonLease"
	CPIGLOBALCATEGORYIDNONLEASE="CpiGlobalCategoryIdNonLease"
	CURRENTINDEXLEVELNONLEASE="CurrentIndexLevelNonLease"
	INDEXATIONREFERENCEDATENONLEASE="IndexationReferenceDateNonLease"
	CONDITIONALINDEXATIONNONLEASE="ConditionalIndexationNonLease"
	MINIMUMPERCENTAGECHANGENONLEASE="MinimumPercentageChangeNonLease"
	MAXIMUMPERCENTAGECHANGENONLEASE="MaximumPercentageChangeNonLease"
	CALCULATETAX="CalculateTax"
	AUTOMONTHTOMONTH="AutoMonthToMonth"

class TermsColumns(Enum):
	LEASEID="LeaseId"
	TERMID="TermId"
	STARTDATE="StartDate"
	ENDDATE="EndDate"
	AMOUNTFREQUENCY="AmountFrequency"
	PAYMENTFREQUENCY="PaymentFrequency"
	PAYMENTMODE="PaymentMode"
	AREAID="AreaId"
	CURRENCYID="CurrencyId"
	ENDOFMONTHPAYMENT="EndOfMonthPayment"
	PRORATA="ProRata"
	EXPENSECATEGORYID="ExpenseCategoryId"
	FIRSTPAYMENTDATE="FirstPaymentDate"
	NOTE="Note"

class TermAmountsColumns(Enum):
	TERMID="TermId"
	LEGACY="Legacy"
	STARTDATE="StartDate"
	ENDDATE="EndDate"
	AMOUNT="Amount"
	HOLD="Hold"
	FIRSTSPECIALPAYMENTDATE="FirstSpecialPaymentDate"
	LASTSPECIALPAYMENTDATE="LastSpecialPaymentDate"
	FIRSTPAYMENTAMOUNT="FirstPaymentAmount"
	LASTPAYMENTAMOUNT="LastPaymentAmount"
	FIRSTPROVISIONINGAMOUNT="FirstProvisioningAmount"
	LASTPROVISIONINGAMOUNT="LastProvisioningAmount"
	RATE="Rate"
	TERMINDEXATIONTYPE="TermIndexationType"

class TermVendorColumns(Enum):
	TERMID="TermId"
	VENDORID="VendorId"
	OWNERSHIP="Ownership"

class NfsLinkColumns(Enum):
	NFSLINKID="NfsLinkId"
	LEASEID="LeaseId"
	MASTERAGREEMENTID="MasterAgreementId"
	CONTRACTID="ContractId"
	LEASECOMPONENTID="LeaseComponentId"
	ACTIVATIONGROUPID="ActivationGroupId"

class PercentageRentPeriodColumns(Enum):
	LEASEID="LeaseId"
	PERCENTAGERENTPERIODID="PercentageRentPeriodId"
	DATEFROM="DateFrom"
	DATETO="DateTo"

class PercentageRentExclusionColumns(Enum):
	PERCENTAGERENTPERIODID="PercentageRentPeriodId"
	SALECATEGORY="SaleCategory"
	SALESUBCATEGORY="SaleSubCategory"

class PercentageRentRuleColumns(Enum):
	PERCENTAGERENTPERIODID="PercentageRentPeriodId"
	CATEGORY="Category"
	SUBCATEGORY="SubCategory"
	MINIMUMPERYEAR="MinimumPerYear"
	MAXIMUMPERYEAR="MaximumPerYear"
	ADJUSTMENTFREQUENCY="AdjustmentFrequency"
	PAYMENTFREQUENCY="PaymentFrequency"
	EXPENSECATEGORIES="ExpenseCategories"
	CHARGEEXPENSECATEGORIES="ChargeExpenseCategories"
	CALCULATIONMODE="CalculationMode"
	BREAKEVENPOINTTYPE="BreakevenPointType"
	BREAKEVENPOINTPERCENTAGE="BreakevenPointPercentage"
	BRACKETS="Brackets"
	FORMULA="Formula"
	NOTE="Note"

class LeaseClauseTypeColumns(Enum):
	LEASEID="LeaseId"
	LEASECLAUSETYPEID="LeaseClauseTypeId"
	TYPE="Type"
	ISNOTAPPLICABLE="IsNotApplicable"

class ClauseColumns(Enum):
	LEASECLAUSETYPEID="LeaseClauseTypeId"
	CLAUSEID="ClauseId"
	PAGE="Page"
	RENTORCOST="RentOrCost"
	SECTION="Section"

class LeaseCriticalClauseTypeColumns(Enum):
	LEASEID="LeaseId"
	LEASECRITICALCLAUSETYPEID="LeaseCriticalClauseTypeId"
	TYPE="Type"
	ISNOTAPPLICABLE="IsNotApplicable"

class CriticalClauseColumns(Enum):
	LEASECRITICALCLAUSETYPEID="LeaseCriticalClauseTypeId"
	CRITICALCLAUSEID="CriticalClauseId"
	STARTDATE="StartDate"
	ENDDATE="EndDate"
	EARLYNOTICEDATE="EarlyNoticeDate"
	EXERCISED="Exercised"
	INCREASETYPE="IncreaseType"
	LATESTNOTICEDATE="LatestNoticeDate"
	NOTIFICATIONDATE="NotificationDate"
	PAGE="Page"
	RENTORCOST="RentOrCost"
	SECTION="Section"
	RENTTYPE="RentType"
	EXERCISEMETHOD="ExerciseMethod"

class InsuranceColumns(Enum):
	LEASEID="LeaseId"
	INSURANCEID="InsuranceId"
	TYPE="Type"
	AMOUNT="Amount"
	PAGE="Page"
	SECTION="Section"

class LeaseConditionColumns(Enum):
	LEASEID="LeaseId"
	LEASECONDITIONID="LeaseConditionId"
	REPLACEDBY="ReplacedBy"
	MANAGEDBY="ManagedBy"
	PAIDBY="PaidBy"
	TYPE="Type"
	STARTDATE="StartDate"
	ENDDATE="EndDate"
	ADMINFEE="AdminFee"
	FIXEDINCREASEPERCENTAGE="FixedIncreasePercentage"
	PAGE="Page"
	SECTION="Section"
	NOTE="Note"
	PROSHAREID="ProShareId"
	CAPID="CAPId"

class AreaBasedProShareColumns(Enum):
	AREABASEDPROSHAREID="AreaBasedProShareId"
	DIVIDENDAREATYPE="DividendAreaType"
	DIVISORAREATYPE="DivisorAreaType"

class FixedPercentageProShareColumns(Enum):
	FIXEDPERCENTAGEPROSHAREID="FixedPercentageProShareId"
	FIXEDPERCENTAGE="FixedPercentage"

class FixedCAPColumns(Enum):
	FIXEDCAPID="FixedCAPId"
	AMOUNT="Amount"

class OverBaseCAPColumns(Enum):
	OVERBASECAPID="OverBaseCAPId"
	BASEYEAR="BaseYear"
	BASEAMOUNT="BaseAmount"
	MAXINCREASEPERCENTAGE="MaxIncreasePercentage"
	CUMULATIVE="Cumulative"

class OverYearCAPColumns(Enum):
	OVERYEARCAPID="OverYearCAPId"
	BASEYEAR="BaseYear"
	BASEAMOUNT="BaseAmount"
	MAXINCREASEPERCENTAGE="MaxIncreasePercentage"
	CUMULATIVE="Cumulative"

class LeaseIncentiveColumns(Enum):
	LEASEID="LeaseId"
	LEASEINCENTIVEID="LeaseIncentiveId"
	TYPE="Type"
	TOTALAMOUNT="TotalAmount"
	PAGE="Page"
	SECTION="Section"

class DrawColumns(Enum):
	DRAWID="DrawId"
	TRIGGER="Trigger"
	FOLLOWUPDATE="FollowUpDate"
	PERCENTAGE="Percentage"
	INVOICEDAMOUNT="InvoicedAmount"
	RECEIVEDAMOUNT="ReceivedAmount"
	INVOICEDDATE="InvoicedDate"
	RECEIVEDDATE="ReceivedDate"
	NOTE="Note"
	LEASEINCENTIVEID="LeaseIncentiveId"
	DRAWNUMBER="DrawNumber"

class UserDefinedFieldsColumns(Enum):
	OBJECTTYPE="ObjectType"
	OBJECTID="ObjectId"
	GROUP="Group"
	SUBGROUP="SubGroup"
	FIELD="Field"
	FIELDTYPE="FieldType"
	FIELDVALUE="FieldValue"

class LeaseEventColumns(Enum):
	LEASEID="LeaseId"
	TYPE="Type"
	ACTIVITYDATE="ActivityDate"
	DETAIL="Detail"
	CODE="Code"
	RELATEDOPTION="RelatedOption"

class DocumentLinkColumns(Enum):
	LINK="Link"
	ENTITY="Entity"
	ENTITYID="EntityId"
	TITLE="Title"
	DESCRIPTION="Description"
	SIGNEDDATE="SignedDate"
	STATUS="Status"
	DOCUMENTTYPE="DocumentType"

class NoteColumns(Enum):
	ENTITYTYPE="EntityType"
	ENTITYID="EntityId"
	MESSAGE="Message"

class NoteEntityTypeOptionColumns(Enum):
	PREMISE="Premise"

class DocumentEntitiesColumns(Enum):
	LOCATION="Location"

SHEET_COLUMNS_MAPPING  = {
	SheetName.LOCATION : LocationColumns,
	SheetName.LOCATIONGROUP : LocationGroupColumns,
	SheetName.LOCATIONLEGALENTITY : LocationLegalEntityColumns,
	SheetName.LOCATIONAREA : LocationAreaColumns,
	SheetName.LOCATIONAREAHISTORY : LocationAreaHistoryColumns,
	SheetName.LOCATIONTOPARTNER : LocationToPartnerColumns,
	SheetName.LOCATIONTOPARTNERCONTACT : LocationToPartnerContactColumns,
	SheetName.OPERATINGCOSTPERIOD : OperatingCostPeriodColumns,
	SheetName.OPERATINGCOSTPERIODEXPENSE : OperatingCostPeriodExpenseColumns,
	SheetName.PREMISE : PremiseColumns,
	SheetName.PREMISEAREA : PremiseAreaColumns,
	SheetName.PREMISEAREAHISTORY : PremiseAreaHistoryColumns,
	SheetName.PREMISEGROUP : PremiseGroupColumns,
	SheetName.LEASE : LeaseColumns,
	SheetName.TERMS : TermsColumns,
	SheetName.TERMAMOUNTS : TermAmountsColumns,
	SheetName.TERMVENDOR : TermVendorColumns,
	SheetName.NFSLINK : NfsLinkColumns,
	SheetName.PERCENTAGERENTPERIOD : PercentageRentPeriodColumns,
	SheetName.PERCENTAGERENTEXCLUSION : PercentageRentExclusionColumns,
	SheetName.PERCENTAGERENTRULE : PercentageRentRuleColumns,
	SheetName.LEASECLAUSETYPE : LeaseClauseTypeColumns,
	SheetName.CLAUSE : ClauseColumns,
	SheetName.LEASECRITICALCLAUSETYPE : LeaseCriticalClauseTypeColumns,
	SheetName.CRITICALCLAUSE : CriticalClauseColumns,
	SheetName.INSURANCE : InsuranceColumns,
	SheetName.LEASECONDITION : LeaseConditionColumns,
	SheetName.AREABASEDPROSHARE : AreaBasedProShareColumns,
	SheetName.FIXEDPERCENTAGEPROSHARE : FixedPercentageProShareColumns,
	SheetName.FIXEDCAP : FixedCAPColumns,
	SheetName.OVERBASECAP : OverBaseCAPColumns,
	SheetName.OVERYEARCAP : OverYearCAPColumns,
	SheetName.LEASEINCENTIVE : LeaseIncentiveColumns,
	SheetName.DRAW : DrawColumns,
	SheetName.USERDEFINEDFIELDS : UserDefinedFieldsColumns,
	SheetName.LEASEEVENT : LeaseEventColumns,
	SheetName.DOCUMENTLINK : DocumentLinkColumns,
	SheetName.NOTE : NoteColumns,
	SheetName.NOTEENTITYTYPEOPTION : NoteEntityTypeOptionColumns,
	SheetName.DOCUMENTENTITIES : DocumentEntitiesColumns,
}
