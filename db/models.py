from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Table: Funds
class Fund(Base):
    __tablename__ = 'funds'
    fund_id = Column(Integer, primary_key=True)
    official_name = Column(String, nullable=False)
    marketing_name = Column(String, nullable=False)
    asset_class = Column(String, nullable=False)
    legal_structure = Column(String, nullable=False)
    creation_date = Column(Date, nullable=False)
    closure_date = Column(Date)
    status = Column(String, nullable=False)
    esg = Column(Boolean)
    sfdr_article = Column(String)
    portfolio_manager = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    valuation = Column(String, nullable=False)
    management_company = Column(String, nullable=False)
    distribution_company = Column(String, nullable=False)
    benchmark_indicator = Column(String, nullable=False)

    # Relationships
    fund_codes = relationship("FundCode", back_populates="fund")
    benchmarks = relationship("Benchmark", back_populates="fund")
    share_classes = relationship("ShareClass", back_populates="fund")
    productions = relationship("Production", back_populates="fund")


# Table: Fund Codes
class FundCode(Base):
    __tablename__ = 'fund_codes'
    fund_code_id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.fund_id'))
    code = Column(String, nullable=False)
    portfolio_code = Column(String)
    portfolio_code_apo = Column(String)
    portfolio_code_tr = Column(String)
    cam_id = Column(String)
    lei = Column(String)

    # Relationship
    fund = relationship("Fund", back_populates="fund_codes")


# Table: Benchmarks
class Benchmark(Base):
    __tablename__ = 'benchmarks'
    benchmark_id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.fund_id'))
    name = Column(String, nullable=False)
    indices = Column(String, nullable=False)

    # Relationship
    fund = relationship("Fund", back_populates="benchmarks")


# Table: Share Classes
class ShareClass(Base):
    __tablename__ = 'share_classes'
    share_class_id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.fund_id'))
    short_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    share_class_type = Column(String, nullable=False)
    distribution = Column(String, nullable=False)

    # Relationships
    fund = relationship("Fund", back_populates="share_classes")
    share_class_codes = relationship("ShareClassCode", back_populates="share_class")


# Table: Share Class Codes
class ShareClassCode(Base):
    __tablename__ = 'share_class_codes'
    share_class_code_id = Column(Integer, primary_key=True)
    share_class_id = Column(Integer, ForeignKey('share_classes.share_class_id'))
    code = Column(String, nullable=False)
    isin = Column(String, nullable=False)
    series_code = Column(String, nullable=False)
    gfc_fund = Column(String, nullable=False)

    # Relationship
    share_class = relationship("ShareClass", back_populates="share_class_codes")


# Table: Production
class Production(Base):
    __tablename__ = 'productions'
    production_id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.fund_id'))
    share_class_id = Column(Integer, ForeignKey('share_classes.share_class_id'))
    potential_data_source = Column(String)
    comment = Column(Text)
    output_file_name = Column(String)
    due_days = Column(Integer)
    production_type = Column(String)
    data_point = Column(String)
    language = Column(String)
    country_distribution = Column(String)
    recipient = Column(String)
    distribution_mode = Column(String)
    data_source_used = Column(String)
    pm_validation = Column(Boolean)

    # Relationships
    fund = relationship("Fund", back_populates="productions")
    share_class = relationship("ShareClass")


# Table: Merger
class Merger(Base):
    __tablename__ = 'mergers'
    merger_id = Column(Integer, primary_key=True)
    production_id = Column(Integer, ForeignKey('productions.production_id'))
    output_file_name = Column(String)
    frequency = Column(String)
    country = Column(String)
    language = Column(String)
    page_cover = Column(Boolean)
    page_cover_s = Column(Boolean)
    page_esg = Column(Boolean)
    page_esg_s = Column(Boolean)
    page_performance = Column(Boolean)
    page_performance_s = Column(Boolean)
    page_allocation = Column(Boolean)
    page_allocation_s = Column(Boolean)
    page_comments = Column(Boolean)
    page_comments_s = Column(Boolean)
    page_attribution = Column(Boolean)
    page_attribution_s = Column(Boolean)
    page_order = Column(Integer)
    order_performance = Column(Integer)
    merge_ready = Column(Boolean)
    merge_date = Column(Date)

    # Relationship
    production = relationship("Production")


# Table: Scheduler Parameters
class SchedulerParam(Base):
    __tablename__ = 'scheduler_params'
    scheduler_param_id = Column(Integer, primary_key=True)
    crystal_template_id = Column(Integer)
    template_name = Column(String)
    is_local = Column(Boolean)
    is_series = Column(Boolean)
    is_retail = Column(Boolean)
    report_date = Column(Boolean)
    rw_date = Column(Boolean)
    reporting_periodicity = Column(Boolean)
    esg_carb_emission = Column(Boolean)
    distribution_zone = Column(Boolean)
    article_173_indicator = Column(Boolean)
    generate_pdf = Column(Boolean)


# Table: Technical Tables
class TechnicalTable(Base):
    __tablename__ = 'technical_tables'
    tt_id = Column(Integer, primary_key=True)
    tt_category = Column(String, nullable=False)
    tt_value = Column(String, nullable=False)


class TechnicalTableFrequency(Base):
    __tablename__ = 'technical_table_frequencies'
    tt_fr_id = Column(Integer, primary_key=True)
    tt_id = Column(Integer, ForeignKey('technical_tables.tt_id'))
    tt_value = Column(String, nullable=False)

    # Relationship
    technical_table = relationship("TechnicalTable")


# Table: Holidays
class Holiday(Base):
    __tablename__ = 'holidays'
    holiday_id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)


# Table: Data Points
class DataPoint(Base):
    __tablename__ = 'data_points'
    data_point_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    data_source = Column(String)
    provider = Column(String)
    methodology = Column(String)


# Table: Data Point Categories
class DataPointCategory(Base):
    __tablename__ = 'data_point_categories'
    data_point_category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)

    # Relationships
    data_points = relationship("DataPoint")


# Table: Production Data Points (relationship table)
class ProductionDataPoint(Base):
    __tablename__ = 'production_data_points'
    production_data_point_id = Column(Integer, primary_key=True)
    production_id = Column(Integer, ForeignKey('productions.production_id'))
    data_point_id = Column(Integer, ForeignKey('data_points.data_point_id'))

    # Relationships
    production = relationship("Production")
    data_point = relationship("DataPoint")


# Table: Production Groups
class ProductionGroup(Base):
    __tablename__ = 'production_groups'
    production_group_id = Column(Integer, primary_key=True)
    group_name = Column(String, nullable=False)


class ProductionGroupRelation(Base):
    __tablename__ = 'production_group_relations'
    production_group_relation_id = Column(Integer, primary_key=True)
    production_group_id = Column(Integer, ForeignKey('production_groups.production_group_id'))
    production_id = Column(Integer, ForeignKey('productions.production_id'))

    # Relationships
    production_group = relationship("ProductionGroup")
    production = relationship("Production")


# Table: Dashboards (dynamic data)
class Dashboard(Base):
    __tablename__ = 'dashboards'
    dashboard_id = Column(Integer, primary_key=True)
    production_id = Column(Integer, ForeignKey('productions.production_id'))
    historical_status = Column(String, nullable=False)

    # Relationship
    production = relationship("Production")


# Table: Holidays History (dynamic data)
class HolidayHistory(Base):
    __tablename__ = 'holiday_histories'
    holiday_history_id = Column(Integer, primary_key=True)
    holiday_id = Column(Integer, ForeignKey('holidays.holiday_id'))
    historical_status = Column(String, nullable=False)

    # Relationship
    holiday = relationship("Holiday")


def setup_database():
    engine = create_engine('sqlite:///your_database.db')
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    setup_database()
