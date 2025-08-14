from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, unique=True, index=True, nullable=True)
    timestamp = Column(String)
    email = Column(String)
    required_by = Column(String)
    requirement_type = Column(String)
    division = Column(String)
    category = Column(String)
    requirement_details = Column(Text)
    priority = Column(String)
    customer_name = Column(String)
    remark = Column(Text)
    ticket_type = Column(String)
    target_date = Column(String)
    company_name = Column(String)
    tt_assign_to = Column(String)
    tt_assigned_date = Column(String)
    status = Column(String)
    proposed_grade = Column(String)
    proposed_reason = Column(Text)
    notes = Column(Text)
    cc_email = Column(String)
    zone = Column(String)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lspl_grade = Column(String, unique=True, index=True)
    division = Column(String)      # e.g., Die Casting, Forging
    category = Column(String)      # e.g., Die Lube, Flux, etc.
    compatible_process = Column(String)  # free text tags
    metal = Column(String)         # e.g., Al, Mg, Steel
    temp_min_c = Column(Float)     # Optional spec
    temp_max_c = Column(Float)
    notes = Column(Text)

class RnDRecord(Base):
    __tablename__ = "rnd_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lspl_grade = Column(String, index=True)
    spec_summary = Column(Text)     # free text description
    flags = Column(String)          # e.g., "low-residue; high-lubricity"
    constraints = Column(Text)      # e.g., "RO water only; hardness < 120 ppm"

class TrialRecord(Base):
    __tablename__ = "trial_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, index=True)
    lspl_grade = Column(String, index=True)
    conditions = Column(Text)       # serialized summary of parameters
    outcome = Column(String)        # e.g., "success", "mixed", "fail"
    notes = Column(Text)

class ComplaintRecord(Base):
    __tablename__ = "complaint_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, index=True)
    lspl_grade = Column(String, index=True)
    conditions = Column(Text)
    issue = Column(Text)
    severity = Column(String)       # e.g., "low", "high"
