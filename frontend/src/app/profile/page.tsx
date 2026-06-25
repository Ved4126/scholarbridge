"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { Navbar } from "@/components/Navbar";
import { ProfileFormSection } from "@/components/ProfileFormSection";
import { ErrorAlert } from "@/components/ErrorAlert";
import { createProfile, scoreAll, ProfileApiError } from "@/lib/api";
import { Loader2 } from "lucide-react";


interface ProfileFormData {
  full_name: string;
  date_of_birth: string;
  gender: string;
  nationality: string;
  home_country: string;
  home_city: string;
  residence_country: string;
  residence_state: string;
  residence_city: string;
  university_name: string;
  degree_level: "undergrad" | "masters" | "phd" | "postdoc";
  field_of_study: string;
  minor: string;
  university_city: string;
  university_state: string;
  university_country: string;
  gpa: number;
  gpa_scale: number;
  expected_graduation_year: number;
  first_generation_student: boolean | string;
  gre: string | number;
  gmat: string | number;
  toefl: string | number;
  ielts: string | number;
  sat: string | number;
  act: string | number;
  visa_type: string;
  enrollment_status: "full_time" | "part_time";
  published_research: boolean | string;
  research_papers: string;
  citations_count: string | number;
  conference_presentations: number;
  patents: number;
  academic_awards: string;
  previous_scholarships: string;
  leadership_roles: string;
  volunteer_hours: string | number;
  sports_achievements: string;
  artistic_achievements: string;
  entrepreneurship_experience: boolean | string;
  financial_need_level: "low" | "medium" | "high";
  family_income_bracket: string;
  current_funding_sources: string;
  dependents: string | number;
}

export default function ProfileFormPage() {
  const router = useRouter();
  const [apiError, setApiError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    defaultValues: {
      full_name: "",
      date_of_birth: "",
      gender: "",
      nationality: "",
      home_country: "",
      home_city: "",
      residence_country: "",
      residence_state: "",
      residence_city: "",
      university_name: "",
      degree_level: "undergrad",
      field_of_study: "",
      minor: "",
      university_city: "",
      university_state: "",
      university_country: "",
      gpa: 4.0,
      gpa_scale: 4.0,
      expected_graduation_year: new Date().getFullYear() + 2,
      first_generation_student: "false",
      gre: "",
      gmat: "",
      toefl: "",
      ielts: "",
      sat: "",
      act: "",
      visa_type: "",
      enrollment_status: "full_time",
      published_research: "false",
      research_papers: "",
      citations_count: "",
      conference_presentations: 0,
      patents: 0,
      academic_awards: "",
      previous_scholarships: "",
      leadership_roles: "",
      volunteer_hours: "",
      sports_achievements: "",
      artistic_achievements: "",
      entrepreneurship_experience: "false",
      financial_need_level: "medium",
      family_income_bracket: "",
      current_funding_sources: "",
      dependents: "",
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    setIsSubmitting(true);
    setApiError(null);

    try {
      // Parse values according to StudentProfile specifications
      const payload: Record<string, unknown> = {
        ...data,
        gpa: typeof data.gpa === "string" ? parseFloat(data.gpa) : data.gpa,
        gpa_scale: typeof data.gpa_scale === "string" ? parseFloat(data.gpa_scale) : data.gpa_scale,
        expected_graduation_year: typeof data.expected_graduation_year === "string" ? parseInt(data.expected_graduation_year) : data.expected_graduation_year,
        conference_presentations: typeof data.conference_presentations === "string" ? parseInt(data.conference_presentations) : data.conference_presentations,
        patents: typeof data.patents === "string" ? parseInt(data.patents) : data.patents,
        published_research: data.published_research === "true" || data.published_research === true,
        entrepreneurship_experience: data.entrepreneurship_experience === "true" || data.entrepreneurship_experience === true,
        first_generation_student: data.first_generation_student === "true" || data.first_generation_student === true,
      };

      // Handle GPA validation check
      if ((payload.gpa as number) > (payload.gpa_scale as number)) {
        throw new Error("GPA cannot be greater than GPA Scale.");
      }

      // Clean/sanitize enrollment_status
      const enrollmentStatus = data.enrollment_status;
      if (enrollmentStatus) {
        const cleaned = enrollmentStatus.toLowerCase().replace("-", "_").trim();
        if (cleaned === "full_time" || cleaned === "fulltime") {
          payload.enrollment_status = "full_time";
        } else if (cleaned === "part_time" || cleaned === "parttime") {
          payload.enrollment_status = "part_time";
        } else {
          payload.enrollment_status = enrollmentStatus;
        }
      }

      // Clean/sanitize visa_type
      const visaType = data.visa_type;
      if (visaType) {
        const trimmed = visaType.trim();
        if (trimmed.toLowerCase() === "f1") {
          payload.visa_type = "F-1";
        } else if (trimmed.toLowerCase() === "j1") {
          payload.visa_type = "J-1";
        } else if (trimmed.toLowerCase() === "h1b") {
          payload.visa_type = "H-1B";
        } else {
          payload.visa_type = trimmed;
        }
      }

      // Clean/sanitize degree_level
      const degreeLevel = data.degree_level;
      if (degreeLevel) {
        const cleaned = degreeLevel.toLowerCase().trim();
        if (cleaned.includes("undergrad")) {
          payload.degree_level = "undergrad";
        } else if (cleaned.includes("master")) {
          payload.degree_level = "masters";
        } else if (cleaned.includes("phd")) {
          payload.degree_level = "phd";
        } else if (cleaned.includes("postdoc")) {
          payload.degree_level = "postdoc";
        } else {
          payload.degree_level = degreeLevel;
        }
      }

      // Convert optional string inputs to appropriate types
      if (data.gender === "") payload.gender = null;
      if (data.home_city === "") payload.home_city = null;
      if (data.residence_state === "") payload.residence_state = null;
      if (data.residence_city === "") payload.residence_city = null;
      if (data.minor === "") payload.minor = null;
      if (data.family_income_bracket === "") payload.family_income_bracket = null;

      // Numbers
      payload.gre = data.gre ? parseFloat(data.gre as string) : null;
      payload.gmat = data.gmat ? parseFloat(data.gmat as string) : null;
      payload.toefl = data.toefl ? parseFloat(data.toefl as string) : null;
      payload.ielts = data.ielts ? parseFloat(data.ielts as string) : null;
      payload.sat = data.sat ? parseFloat(data.sat as string) : null;
      payload.act = data.act ? parseFloat(data.act as string) : null;
      payload.volunteer_hours = data.volunteer_hours ? parseInt(data.volunteer_hours as string) : null;
      payload.dependents = data.dependents ? parseInt(data.dependents as string) : null;
      payload.citations_count = data.citations_count ? parseInt(data.citations_count as string) : null;

      payload.field_of_study = data.field_of_study;
      payload.major = data.field_of_study;

      // Handle lists (comma separated values parsed to string lists)
      const parseList = (str: string) => str ? str.split(",").map(s => s.trim()).filter(Boolean) : [];
      payload.research_papers = data.research_papers ? parseList(data.research_papers) : null;
      payload.academic_awards = parseList(data.academic_awards);
      payload.previous_scholarships = parseList(data.previous_scholarships);
      payload.leadership_roles = parseList(data.leadership_roles);
      payload.sports_achievements = parseList(data.sports_achievements);
      payload.artistic_achievements = parseList(data.artistic_achievements);
      payload.current_funding_sources = parseList(data.current_funding_sources);

      console.log("Constructed payload for submission:", payload);

      // Call profile creation API
      const profileResult = await createProfile(payload);

      // Call score evaluation API
      const matches = await scoreAll(profileResult.profile_id);


       // Save scoring results to session storage
      sessionStorage.setItem("scholarship_results", JSON.stringify(matches));
      sessionStorage.setItem("profile_completeness", String(profileResult.completeness));
      sessionStorage.setItem("profile_id", profileResult.profile_id);
      sessionStorage.setItem("active_profile", JSON.stringify(payload));

      // Redirect to results
      router.push("/results");
    } catch (err: unknown) {
      console.error("Profile submission error:", err);
      const profileApiErr = err as ProfileApiError;
      if (profileApiErr.details) {
        let errorMsg = "Validation details:\n";
        if (Array.isArray(profileApiErr.details)) {
          const detailStrings = (profileApiErr.details as Array<{ loc?: unknown[]; msg?: string }>).map((d) => {
            const fieldPath = Array.isArray(d.loc) ? d.loc.filter((loc) => loc !== "body").join(".") : "";
            const prefix = fieldPath ? `"${fieldPath}": ` : "";
            return `${prefix}${d.msg || JSON.stringify(d)}`;
          });
          errorMsg += detailStrings.join("\n");
        } else if (typeof profileApiErr.details === "object") {
          errorMsg += JSON.stringify(profileApiErr.details, null, 2);
        } else {
          errorMsg += String(profileApiErr.details);
        }
        setApiError(errorMsg);
      } else {
        setApiError(profileApiErr.message || "An unexpected network error occurred.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      <Navbar />
      <main id="main-content" className="flex-grow max-w-4xl mx-auto w-full px-4 sm:px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Tell us about yourself</h1>
          <p className="text-sm text-slate-600 mt-2">
            Complete the form sections below. Fields marked with <span className="text-red-500 font-bold">*</span> are required.
          </p>
        </div>


        {apiError && (
          <ErrorAlert message={apiError} onRetry={handleSubmit(onSubmit)} />
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Section 1: Personal */}
          <ProfileFormSection
            title="1. Personal Details"
            description="Basic information about your nationality and country of residence."
          >
            <div className="flex flex-col gap-1.5">
              <label htmlFor="full_name" className="text-sm font-semibold text-slate-700">
                Full Name <span className="text-red-500">*</span>
              </label>
              <input
                id="full_name"
                type="text"
                {...register("full_name", { required: "Full name is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.full_name && (
                <span className="text-xs text-red-600">{errors.full_name.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="date_of_birth" className="text-sm font-semibold text-slate-700">
                Date of Birth <span className="text-red-500">*</span>
              </label>
              <input
                id="date_of_birth"
                type="date"
                {...register("date_of_birth", { required: "Date of birth is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.date_of_birth && (
                <span className="text-xs text-red-600">{errors.date_of_birth.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="gender" className="text-sm font-semibold text-slate-700">
                Gender <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <select
                id="gender"
                {...register("gender")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none bg-white"
              >
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="non_binary">Non-binary</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="nationality" className="text-sm font-semibold text-slate-700">
                Nationality (ISO 2-letter Code) <span className="text-red-500">*</span>
              </label>
              <input
                id="nationality"
                type="text"
                maxLength={2}
                placeholder="e.g. IN, CN, NG"
                {...register("nationality", { required: "Nationality is required", maxLength: 2 })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none uppercase"
              />
              {errors.nationality && (
                <span className="text-xs text-red-600">{errors.nationality.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="home_country" className="text-sm font-semibold text-slate-700">
                Home Country <span className="text-red-500">*</span>
              </label>
              <input
                id="home_country"
                type="text"
                {...register("home_country", { required: "Home country is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.home_country && (
                <span className="text-xs text-red-600">{errors.home_country.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="home_city" className="text-sm font-semibold text-slate-700">
                Home City <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                id="home_city"
                type="text"
                {...register("home_city")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="residence_country" className="text-sm font-semibold text-slate-700">
                Current Residence Country <span className="text-red-500">*</span>
              </label>
              <input
                id="residence_country"
                type="text"
                placeholder="e.g. United States"
                {...register("residence_country", { required: "Current residence country is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.residence_country && (
                <span className="text-xs text-red-600">{errors.residence_country.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="residence_state" className="text-sm font-semibold text-slate-700">
                Current Residence State <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                id="residence_state"
                type="text"
                placeholder="e.g. CA"
                {...register("residence_state")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="residence_city" className="text-sm font-semibold text-slate-700">
                Current Residence City <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                id="residence_city"
                type="text"
                placeholder="e.g. Stanford"
                {...register("residence_city")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>
          </ProfileFormSection>

          {/* Section 2: Academic */}
          <ProfileFormSection
            title="2. Academic Qualifications"
            description="Your current degree program, university details, and GPA scores."
          >
            <div className="flex flex-col gap-1.5">
              <label htmlFor="university_name" className="text-sm font-semibold text-slate-700">
                University Name <span className="text-red-500">*</span>
              </label>
              <input
                id="university_name"
                type="text"
                {...register("university_name", { required: "University name is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.university_name && (
                <span className="text-xs text-red-600">{errors.university_name.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="degree_level" className="text-sm font-semibold text-slate-700">
                Degree Level <span className="text-red-500">*</span>
              </label>
              <select
                id="degree_level"
                {...register("degree_level", { required: true })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none bg-white"
              >
                <option value="undergrad">Undergraduate</option>
                <option value="masters">Master&apos;s</option>
                <option value="phd">PhD</option>
                <option value="postdoc">Postdoc</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="field_of_study" className="text-sm font-semibold text-slate-700">
                Major / Field of Study <span className="text-red-500">*</span>
              </label>
              <input
                id="field_of_study"
                type="text"
                placeholder="e.g. Computer Science"
                {...register("field_of_study", { required: "Major/Field of study is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.field_of_study && (
                <span className="text-xs text-red-600">{errors.field_of_study.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="minor" className="text-sm font-semibold text-slate-700">
                Minor <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                id="minor"
                type="text"
                {...register("minor")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="university_city" className="text-sm font-semibold text-slate-700">
                University City <span className="text-red-500">*</span>
              </label>
              <input
                id="university_city"
                type="text"
                placeholder="e.g. Stanford"
                {...register("university_city", { required: "University city is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.university_city && (
                <span className="text-xs text-red-600">{errors.university_city.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="university_state" className="text-sm font-semibold text-slate-700">
                University State / Province <span className="text-red-500">*</span>
              </label>
              <input
                id="university_state"
                type="text"
                placeholder="e.g. CA"
                {...register("university_state", { required: "University state is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.university_state && (
                <span className="text-xs text-red-600">{errors.university_state.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="university_country" className="text-sm font-semibold text-slate-700">
                University Country <span className="text-red-500">*</span>
              </label>
              <input
                id="university_country"
                type="text"
                placeholder="e.g. United States"
                {...register("university_country", { required: "University country is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.university_country && (
                <span className="text-xs text-red-600">{errors.university_country.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="gpa" className="text-sm font-semibold text-slate-700">
                GPA <span className="text-red-500">*</span>
              </label>
              <input
                id="gpa"
                type="number"
                step="0.01"
                placeholder="3.8"
                {...register("gpa", { required: "GPA is required", min: 0 })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.gpa && (
                <span className="text-xs text-red-600">{errors.gpa.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="gpa_scale" className="text-sm font-semibold text-slate-700">
                GPA Scale <span className="text-red-500">*</span>
              </label>
              <input
                id="gpa_scale"
                type="number"
                step="0.1"
                placeholder="4.0"
                {...register("gpa_scale", { required: "GPA scale is required", min: 0.1 })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.gpa_scale && (
                <span className="text-xs text-red-600">{errors.gpa_scale.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="expected_graduation_year" className="text-sm font-semibold text-slate-700">
                Expected Graduation Year <span className="text-red-500">*</span>
              </label>
              <input
                id="expected_graduation_year"
                type="number"
                {...register("expected_graduation_year", { required: "Graduation year is required", min: 1901, max: 2099 })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.expected_graduation_year && (
                <span className="text-xs text-red-600">{errors.expected_graduation_year.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="first_generation_student" className="text-sm font-semibold text-slate-700">
                First-Generation Student <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <select
                id="first_generation_student"
                {...register("first_generation_student")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none bg-white"
              >
                <option value="false">No</option>
                <option value="true">Yes</option>
              </select>
            </div>
          </ProfileFormSection>

          {/* Section 3: Standardized Tests (Optional Fields) */}
          <ProfileFormSection
            title="3. Test Scores (Optional)"
            description="Optional standardized test results."
          >
            <div className="flex flex-col gap-1.5">
              <label htmlFor="gre" className="text-sm font-semibold text-slate-700">GRE Score</label>
              <input
                id="gre"
                type="number"
                {...register("gre")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="gmat" className="text-sm font-semibold text-slate-700">GMAT Score</label>
              <input
                id="gmat"
                type="number"
                {...register("gmat")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="toefl" className="text-sm font-semibold text-slate-700">TOEFL Score</label>
              <input
                id="toefl"
                type="number"
                {...register("toefl")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="ielts" className="text-sm font-semibold text-slate-700">IELTS Score</label>
              <input
                id="ielts"
                type="number"
                step="0.5"
                {...register("ielts")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="sat" className="text-sm font-semibold text-slate-700">SAT Score</label>
              <input
                id="sat"
                type="number"
                {...register("sat")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="act" className="text-sm font-semibold text-slate-700">ACT Score</label>
              <input
                id="act"
                type="number"
                {...register("act")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>
          </ProfileFormSection>

          {/* Section 4: Visa & Enrollment */}
          <ProfileFormSection
            title="4. Visa & Enrollment status"
            description="Information necessary for determining visa and residency eligibility."
          >
            <div className="flex flex-col gap-1.5">
              <label htmlFor="visa_type" className="text-sm font-semibold text-slate-700">
                Visa Type <span className="text-red-500">*</span>
              </label>
              <input
                id="visa_type"
                type="text"
                placeholder="e.g. F-1, J-1, H-1B"
                {...register("visa_type", { required: "Visa type is required" })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
              {errors.visa_type && (
                <span className="text-xs text-red-600">{errors.visa_type.message}</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="enrollment_status" className="text-sm font-semibold text-slate-700">
                Enrollment Status <span className="text-red-500">*</span>
              </label>
              <select
                id="enrollment_status"
                {...register("enrollment_status", { required: true })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none bg-white"
              >
                <option value="full_time">Full Time</option>
                <option value="part_time">Part Time</option>
              </select>
            </div>
          </ProfileFormSection>

          {/* Section 5: Achievements */}
          <ProfileFormSection
            title="5. Academic & Extracurricular Achievements"
            description="Provide details regarding research, leadership experience, and accomplishments."
          >
            <div className="flex flex-col gap-1.5">
              <label htmlFor="published_research" className="text-sm font-semibold text-slate-700">
                Published Research <span className="text-red-500">*</span>
              </label>
              <select
                id="published_research"
                {...register("published_research", { required: true })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none bg-white"
              >
                <option value="false">No</option>
                <option value="true">Yes</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="citations_count" className="text-sm font-semibold text-slate-700">
                Citations Count <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                id="citations_count"
                type="number"
                placeholder="e.g. 15"
                {...register("citations_count")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="research_papers" className="text-sm font-semibold text-slate-700">
                Research Papers <span className="text-xs text-slate-500 font-normal">(comma-separated)</span>
              </label>
              <input
                id="research_papers"
                type="text"
                placeholder="e.g. Title One, Title Two"
                {...register("research_papers")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="conference_presentations" className="text-sm font-semibold text-slate-700">
                Conference Presentations Count <span className="text-red-500">*</span>
              </label>
              <input
                id="conference_presentations"
                type="number"
                {...register("conference_presentations", { required: true, min: 0 })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="patents" className="text-sm font-semibold text-slate-700">
                Patents Count <span className="text-red-500">*</span>
              </label>
              <input
                id="patents"
                type="number"
                {...register("patents", { required: true, min: 0 })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="entrepreneurship_experience" className="text-sm font-semibold text-slate-700">
                Entrepreneurship Experience <span className="text-red-500">*</span>
              </label>
              <select
                id="entrepreneurship_experience"
                {...register("entrepreneurship_experience", { required: true })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none bg-white"
              >
                <option value="false">No</option>
                <option value="true">Yes</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="leadership_roles" className="text-sm font-semibold text-slate-700">
                Leadership Roles <span className="text-xs text-slate-500 font-normal">(comma-separated)</span>
              </label>
              <input
                id="leadership_roles"
                type="text"
                placeholder="e.g. Student Council President"
                {...register("leadership_roles")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="academic_awards" className="text-sm font-semibold text-slate-700">
                Academic Awards <span className="text-xs text-slate-500 font-normal">(comma-separated)</span>
              </label>
              <input
                id="academic_awards"
                type="text"
                placeholder="e.g. Dean's List 2024"
                {...register("academic_awards")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="previous_scholarships" className="text-sm font-semibold text-slate-700">
                Previous Scholarships <span className="text-xs text-slate-500 font-normal">(comma-separated)</span>
              </label>
              <input
                id="previous_scholarships"
                type="text"
                {...register("previous_scholarships")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="volunteer_hours" className="text-sm font-semibold text-slate-700">
                Volunteer Hours <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                id="volunteer_hours"
                type="number"
                {...register("volunteer_hours")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="sports_achievements" className="text-sm font-semibold text-slate-700">
                Sports Achievements <span className="text-xs text-slate-500 font-normal">(comma-separated)</span>
              </label>
              <input
                id="sports_achievements"
                type="text"
                {...register("sports_achievements")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="artistic_achievements" className="text-sm font-semibold text-slate-700">
                Artistic Achievements <span className="text-xs text-slate-500 font-normal">(comma-separated)</span>
              </label>
              <input
                id="artistic_achievements"
                type="text"
                {...register("artistic_achievements")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>
          </ProfileFormSection>

          {/* Section 6: Financial Need */}
          <ProfileFormSection
            title="6. Financial Details"
            description="Helps us filter matching opportunities requiring financial assistance parameters."
          >
            <div className="flex flex-col gap-1.5 col-span-1 sm:col-span-2">
              <label htmlFor="financial_need_level" className="text-sm font-semibold text-slate-700">
                Financial Need Level <span className="text-red-500">*</span>
              </label>
              <select
                id="financial_need_level"
                {...register("financial_need_level", { required: true })}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none bg-white"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              <span className="text-xs text-slate-500">
                This helps matching logic identify scholarships designed for need-based metrics. This data is kept strictly private.
              </span>
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="family_income_bracket" className="text-sm font-semibold text-slate-700">
                Family Income Bracket <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                id="family_income_bracket"
                type="text"
                placeholder="e.g. 40k-80k"
                {...register("family_income_bracket")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="dependents" className="text-sm font-semibold text-slate-700">
                Number of Dependents <span className="text-xs text-slate-500 font-normal">(optional)</span>
              </label>
              <input
                id="dependents"
                type="number"
                {...register("dependents")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-1.5 col-span-1 sm:col-span-2">
              <label htmlFor="current_funding_sources" className="text-sm font-semibold text-slate-700">
                Current Funding Sources <span className="text-xs text-slate-500 font-normal">(comma-separated)</span>
              </label>
              <input
                id="current_funding_sources"
                type="text"
                placeholder="e.g. TA stipend, Personal savings"
                {...register("current_funding_sources")}
                className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none"
              />
            </div>
          </ProfileFormSection>



          {/* Form Actions */}
          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3.5 text-base font-semibold text-white shadow hover:bg-emerald-500 active:bg-emerald-700 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Analyzing matches...
                </>
              ) : (
                "Find My Scholarships"
              )}
            </button>
          </div>
        </form>
      </main>
      <footer className="bg-slate-900 border-t border-slate-800 py-8 text-center text-xs text-slate-400">
        <p>© {new Date().getFullYear()} ScholarBridge. Built for international student discovery.</p>
      </footer>
    </AppShell>
  );
}
