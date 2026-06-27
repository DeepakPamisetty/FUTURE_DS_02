let
    Source = Csv.Document(
        File.Contents("data/processed/telco_churn_cleaned.csv"),
        [Delimiter = ",", Columns = 25, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"customerID", type text},
            {"gender", type text},
            {"SeniorCitizen", type text},
            {"Partner", type text},
            {"Dependents", type text},
            {"tenure", Int64.Type},
            {"PhoneService", type text},
            {"MultipleLines", type text},
            {"InternetService", type text},
            {"OnlineSecurity", type text},
            {"OnlineBackup", type text},
            {"DeviceProtection", type text},
            {"TechSupport", type text},
            {"StreamingTV", type text},
            {"StreamingMovies", type text},
            {"Contract", type text},
            {"PaperlessBilling", type text},
            {"PaymentMethod", type text},
            {"MonthlyCharges", Currency.Type},
            {"TotalCharges", Currency.Type},
            {"Churn", type text},
            {"ChurnFlag", Int64.Type},
            {"TenureBucket", type text},
            {"MonthlyChargeBucket", type text},
            {"HasProtection", type text}
        }
    )
in
    ChangedTypes
