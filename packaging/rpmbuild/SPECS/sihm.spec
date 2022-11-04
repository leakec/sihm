Name: sihm
Version: 0.0.1
Release:        1%{?dist}
Summary: Standalone Interactive HMTL Movie (SIHM) maker

License:        MIT
URL:           https://github.com/leakec/sihm
Source0:        sihm-%{version}.tar.gz

#BuildRequires:  
#Requires:       
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

%description
Standalone interactive HTML movie installer.

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/usr/share/bash-completions/completions
install _sihm_complete_bash $RPM_BUILD_ROOT/usr/share/bash-completions/completions/_sihm_complete_bash
install -d $RPM_BUILD_ROOT/usr/share/zsh/site-functions
install _sihm_complete_zsh $RPM_BUILD_ROOT/usr/share/zsh/site-functions/_sihm_complete_zsh


%files
/usr/share/zsh/site-functions/_sihm_complete_zsh
/usr/share/bash-completions/completions

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Sun Oct 30 2022 leake test
- 
